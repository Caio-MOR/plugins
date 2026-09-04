"""Testes do validador do marketplace (tools/validar_plugins.py).

Cada gate precisa de um teste que prove que ele REPROVA, não só que passa —
por isso os casos sintéticos abaixo, além do caso "o repo atual passa".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_REPO / "tools"))

import validar_plugins  # noqa: E402


def test_repo_atual_passa():
    erros = validar_plugins.validar(RAIZ_REPO)
    assert erros == [], f"repo atual deveria passar, mas: {erros}"


def _skill_valida(pasta: Path, nome: str) -> None:
    skill_dir = pasta / "plugins" / nome / "skills" / nome
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {nome}\ndescription: uma skill de teste\nformato: cadeia\n---\n\n# {nome}\n",
        encoding="utf-8",
    )
    manifesto_dir = pasta / "plugins" / nome / ".claude-plugin"
    manifesto_dir.mkdir(parents=True)
    (manifesto_dir / "plugin.json").write_text(
        json.dumps({"name": nome, "version": "1.0.0", "description": "teste"}),
        encoding="utf-8",
    )


def _marketplace_valido(pasta: Path, nome: str) -> None:
    mkt_dir = pasta / ".claude-plugin"
    mkt_dir.mkdir(parents=True, exist_ok=True)
    (mkt_dir / "marketplace.json").write_text(
        json.dumps({
            "name": "teste",
            "plugins": [{"name": nome, "source": f"./plugins/{nome}", "version": "1.0.0", "description": "x"}],
        }),
        encoding="utf-8",
    )


def test_skill_sem_formato_reprova(tmp_path: Path):
    nome = "skill-sem-formato"
    _skill_valida(tmp_path, nome)
    _marketplace_valido(tmp_path, nome)
    # remove o campo `formato` do frontmatter recém-criado
    skill_md = tmp_path / "plugins" / nome / "skills" / nome / "SKILL.md"
    texto = skill_md.read_text(encoding="utf-8").replace("formato: cadeia\n", "")
    skill_md.write_text(texto, encoding="utf-8")

    erros = validar_plugins.validar(tmp_path)
    assert any("formato" in e and "SKILL.md" in e for e in erros), erros


def test_caminho_de_maquina_reprova(tmp_path: Path):
    nome = "skill-ok"
    _skill_valida(tmp_path, nome)
    _marketplace_valido(tmp_path, nome)
    (tmp_path / "NOTAS.md").write_text(
        "veja o arquivo em /Users/alguem/projeto/arquivo.txt\n", encoding="utf-8"  # padrao-ouro:ignorar
    )

    erros = validar_plugins.validar(tmp_path)
    assert any("caminho absoluto de máquina" in e for e in erros), erros


def test_caminho_de_maquina_sem_barra_final_reprova(tmp_path: Path):
    # Regressão: /Users/x ou /home/y no fim da linha (sem subpasta depois) também  # padrao-ouro:ignorar
    # é rastro de máquina — a régua antiga exigia uma barra final e deixava passar.
    nome = "skill-ok"
    _skill_valida(tmp_path, nome)
    _marketplace_valido(tmp_path, nome)
    (tmp_path / "NOTAS.md").write_text(
        "usuario: /Users/x\noutra maquina: /home/y\n", encoding="utf-8"  # padrao-ouro:ignorar
    )

    erros = validar_plugins.validar(tmp_path)
    assert any("NOTAS.md:1" in e for e in erros), erros
    assert any("NOTAS.md:2" in e for e in erros), erros


def test_palavra_users_sem_barra_inicial_nao_reprova(tmp_path: Path):
    """`docs/Users/guia.md` não é rastro de máquina: `Users` aqui é nome de pasta do
    projeto, não a home de um usuário — a barra antes de `Users` não é a raiz."""
    nome = "skill-ok"
    _skill_valida(tmp_path, nome)
    _marketplace_valido(tmp_path, nome)
    (tmp_path / "NOTAS.md").write_text(
        "ver docs/Users/guia.md para detalhes\n", encoding="utf-8"
    )

    erros = validar_plugins.validar(tmp_path)
    assert not any("caminho absoluto de máquina" in e for e in erros), erros


def test_marketplace_ausente_reprova(tmp_path: Path):
    erros = validar_plugins.validar(tmp_path)
    assert any("marketplace.json" in e and "não existe" in e for e in erros), erros
