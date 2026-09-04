#!/usr/bin/env python3
"""Validador do marketplace `caio-mor` (Caio-MOR/plugins).

Confere, sem depender do CLI do Claude Code:

1. `.claude-plugin/marketplace.json` é JSON válido, tem `plugins` (lista não vazia).
2. Cada `plugin.json` referenciado é JSON válido, tem `name` e `version`.
3. `name`/`version` do marketplace batem com o `plugin.json` correspondente.
4. Todo `SKILL.md` tem frontmatter YAML válido (mínimo: sem libs externas) com
   `name`, `description` e `formato` preenchidos.
5. Nenhum arquivo versionado contém caminho de máquina (`/Users/`, `/home/`).

Uso: `python tools/validar_plugins.py [RAIZ]` (default: `.`). Exit 0 = ok; 1 = achou
problema; 2 = raiz inválida. Só biblioteca padrão; roda em Windows/Linux/Mac.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

TETO_GIT = 60  # segundos

RE_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---", re.DOTALL)
RE_CAMINHO_MAQUINA = re.compile(
    r"(?i)[a-z]:[\\/]users[\\/]"        # unidade Windows + Users  # padrao-ouro:ignorar
    r"|(?<![\w/])/Users/[A-Za-z0-9_.-]+/"  # home do macOS  # padrao-ouro:ignorar
    r"|(?<![\w/])/home/[A-Za-z0-9_.-]+/"   # home do Linux  # padrao-ouro:ignorar
)
MARCA_IGNORAR = "padrao-ouro:ignorar"

EXT_BINARIAS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp", ".pdf", ".xlsx", ".xlsm",
    ".xls", ".docx", ".pptx", ".zip", ".gz", ".tar", ".7z", ".rar", ".woff", ".woff2",
    ".ttf", ".otf", ".eot", ".pyc", ".exe", ".dll", ".so", ".dylib", ".bin",
})
DIRS_IGNORADOS_NO_DISCO = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv",
                                     ".pytest_cache", ".tmp"})


class Problema(Exception):
    pass


def listar_versionados(raiz: Path) -> list[str]:
    """`git ls-files` quando a raiz é repositório; senão varre o disco."""
    try:
        r = subprocess.run(
            ["git", "-C", str(raiz), "ls-files", "-z"],
            capture_output=True, timeout=TETO_GIT, check=False,
        )
        if r.returncode == 0:
            itens = [p for p in r.stdout.decode("utf-8", errors="replace").split("\0") if p]
            return sorted(p for p in itens if (raiz / p).is_file())
    except (OSError, subprocess.TimeoutExpired):
        pass
    itens = []
    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames[:] = [d for d in dirnames if d not in DIRS_IGNORADOS_NO_DISCO]
        for f in filenames:
            itens.append(Path(dirpath, f).relative_to(raiz).as_posix())
    return sorted(itens)


def ler_texto(raiz: Path, rel: str) -> str | None:
    if Path(rel).suffix.lower() in EXT_BINARIAS:
        return None
    try:
        with open(raiz / rel, "r", encoding="utf-8", errors="replace", newline=None) as fh:
            return fh.read()
    except (OSError, IsADirectoryError):
        return None


class FrontmatterInvalido(Exception):
    pass


def _parse_frontmatter(texto: str) -> dict | None:
    """Frontmatter YAML entre os dois `---`, parseado com PyYAML (YAML de verdade,
    não um recorte de linhas). Levanta `FrontmatterInvalido` se o bloco existe mas o
    YAML é inválido; devolve `None` se não há bloco de frontmatter."""
    m = RE_FRONTMATTER.match(texto)
    if not m:
        return None
    try:
        dados = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise FrontmatterInvalido(str(e)) from e
    return dados if isinstance(dados, dict) else {}


def validar(raiz: Path) -> list[str]:
    erros: list[str] = []
    arquivos = listar_versionados(raiz)
    arquivos_set = set(arquivos)

    # 1) marketplace.json
    mkt_rel = ".claude-plugin/marketplace.json"
    mkt_texto = ler_texto(raiz, mkt_rel) if mkt_rel in arquivos_set else None
    marketplace = None
    if mkt_texto is None:
        erros.append(f"{mkt_rel}: não existe")
    else:
        try:
            marketplace = json.loads(mkt_texto)
        except json.JSONDecodeError as e:
            erros.append(f"{mkt_rel}: JSON inválido ({e.msg})")
        else:
            if not isinstance(marketplace.get("plugins"), list) or not marketplace["plugins"]:
                erros.append(f"{mkt_rel}: sem lista `plugins` não vazia")

    # 2) e 3) plugin.json por entrada do marketplace
    if isinstance(marketplace, dict) and isinstance(marketplace.get("plugins"), list):
        for p in marketplace["plugins"]:
            nome_mkt = p.get("name")
            versao_mkt = p.get("version")
            fonte = str(p.get("source", "")).lstrip("./").rstrip("/")
            manifesto_rel = f"{fonte}/.claude-plugin/plugin.json" if fonte else ".claude-plugin/plugin.json"
            texto = ler_texto(raiz, manifesto_rel) if manifesto_rel in arquivos_set else None
            if texto is None:
                erros.append(f"{manifesto_rel}: não existe (referenciado por {mkt_rel})")
                continue
            try:
                manifesto = json.loads(texto)
            except json.JSONDecodeError as e:
                erros.append(f"{manifesto_rel}: JSON inválido ({e.msg})")
                continue
            for chave in ("name", "version"):
                if not manifesto.get(chave):
                    erros.append(f"{manifesto_rel}: sem `{chave}`")
            if nome_mkt and manifesto.get("name") and nome_mkt != manifesto.get("name"):
                erros.append(
                    f"{manifesto_rel}: `name` ({manifesto.get('name')!r}) difere do marketplace ({nome_mkt!r})"
                )
            if versao_mkt and manifesto.get("version") and versao_mkt != manifesto.get("version"):
                erros.append(
                    f"{manifesto_rel}: `version` ({manifesto.get('version')!r}) difere do marketplace ({versao_mkt!r})"
                )

    # 4) frontmatter de cada SKILL.md
    for rel in arquivos:
        if Path(rel).name != "SKILL.md":
            continue
        texto = ler_texto(raiz, rel) or ""
        try:
            campos = _parse_frontmatter(texto)
        except FrontmatterInvalido as e:
            erros.append(f"{rel}: frontmatter YAML inválido ({e})")
            continue
        if campos is None:
            erros.append(f"{rel}: sem frontmatter (precisa começar e terminar com `---`)")
            continue
        pasta = Path(rel).parent.name
        if str(campos.get("name", "")) != pasta:
            erros.append(f"{rel}: `name` ({campos.get('name')!r}) difere da pasta ({pasta!r})")
        if not str(campos.get("description", "")).strip():
            erros.append(f"{rel}: sem `description`")
        if not str(campos.get("formato", "")).strip():
            erros.append(f"{rel}: sem `formato`")

    # 5) rastro de máquina
    proprio = Path(__file__).name
    for rel in arquivos:
        if Path(rel).name == proprio:
            continue
        texto = ler_texto(raiz, rel)
        if texto is None:
            continue
        for n, linha in enumerate(texto.split("\n"), start=1):
            if MARCA_IGNORAR in linha:
                continue
            if RE_CAMINHO_MAQUINA.search(linha):
                erros.append(f"{rel}:{n}: caminho absoluto de máquina")

    return erros


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    raiz = Path(argv[0]).resolve() if argv else Path(".").resolve()

    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")

    if not raiz.is_dir():
        print(f"raiz inexistente: {raiz}", file=sys.stderr)
        return 2

    erros = validar(raiz)
    if erros:
        print(f"validar_plugins: {len(erros)} problema(s)")
        for e in erros:
            print(f"  {e}")
        return 1
    print("validar_plugins: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
