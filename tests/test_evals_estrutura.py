"""Gate determinístico dos evals de comportamento (R11).

Roda sem LLM: confere estrutura, frontmatter e o mínimo de casos por skill.
A execução com `claude -p` é gate local (`tools/eval_runner.py`), nunca CI —
sem credencial de subscription no runner do CI.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))

import eval_runner  # noqa: E402

RE_CAMINHO_MAQUINA = re.compile(
    r"(?i)[a-z]:[\\/]users[\\/]"
    r"|(?<![\w/])/(Users|home)/[A-Za-z0-9_.-]+(?=[/\s\"'`)\]]|$)"
)


def _plugins():
    mkt = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    return {p["name"]: (RAIZ / str(p["source"]).lstrip("./").rstrip("/")).resolve()
            for p in mkt["plugins"]}


def _casos_por_plugin():
    out = {}
    for nome, plugin_dir in _plugins().items():
        evals_dir = plugin_dir / "evals"
        out[nome] = eval_runner.descobrir_casos(evals_dir, None)
    return out


def test_todo_plugin_do_marketplace_tem_pasta_evals():
    faltando = [nome for nome, d in _plugins().items() if not (d / "evals").is_dir()]
    assert faltando == [], f"plugins sem evals/: {faltando}"


def test_cada_caso_tem_prompt_valido_e_name_igual_a_pasta():
    problemas = []
    for nome, casos in _casos_por_plugin().items():
        for case_dir in casos:
            try:
                caso = eval_runner.parse_caso(case_dir)
            except eval_runner.ErroCasoMalFormado as e:
                problemas.append(str(e))
                continue
            if caso["nome"] != case_dir.name:
                problemas.append(f"{case_dir}: name do frontmatter difere da pasta")
    assert problemas == [], "\n".join(problemas)


def test_cada_skill_tem_ao_menos_3_positivos_e_3_negativos():
    faltando = []
    for nome, casos in _casos_por_plugin().items():
        positivos = 0
        negativos = 0
        for case_dir in casos:
            caso = eval_runner.parse_caso(case_dir)
            tags = set(caso["tags"])
            if "positivo" in tags:
                positivos += 1
            if "negativo" in tags:
                negativos += 1
        if positivos < 3 or negativos < 3:
            faltando.append(f"{nome}: positivos={positivos} negativos={negativos}")
    assert faltando == [], f"skills com menos do que 3+3 casos: {faltando}"


def test_todo_grader_tool_used_tem_regex_compilavel():
    # parse_caso já valida isso (levanta ErroCasoMalFormado); reafirma aqui, explícito.
    problemas = []
    for nome, casos in _casos_por_plugin().items():
        for case_dir in casos:
            caso = eval_runner.parse_caso(case_dir)
            for g in caso["graders"]:
                if g.get("type") == "tool_used":
                    try:
                        re.compile(g["input_match"])
                    except re.error as e:
                        problemas.append(f"{case_dir}/{g['_arquivo']}: {e}")
    assert problemas == [], "\n".join(problemas)


def test_runs_max_turns_timeout_sao_inteiros_positivos():
    # parse_caso já converte e valida; se algum caso não convertesse, levantaria
    # ErroCasoMalFormado aqui mesmo — este teste prova que todos convertem.
    for nome, casos in _casos_por_plugin().items():
        for case_dir in casos:
            caso = eval_runner.parse_caso(case_dir)
            for chave in ("runs", "max_turns", "timeout_seconds"):
                assert isinstance(caso[chave], int) and caso[chave] > 0, f"{case_dir}: {chave}"


def test_prompt_sem_caminho_de_maquina():
    problemas = []
    for nome, casos in _casos_por_plugin().items():
        for case_dir in casos:
            texto = (case_dir / "prompt.md").read_text(encoding="utf-8")
            for n, linha in enumerate(texto.splitlines(), start=1):
                if RE_CAMINHO_MAQUINA.search(linha):
                    problemas.append(f"{case_dir}/prompt.md:{n}: caminho de máquina")
    assert problemas == [], "\n".join(problemas)
