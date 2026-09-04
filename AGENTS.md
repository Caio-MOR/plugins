# caio-mor (plugins) — Instruções para Agentes

tipo: skills

Este arquivo é a fonte única de instruções do repo, em formato multi-vendor ([agents.md](https://agents.md/)). O `CLAUDE.md` da raiz o importa e guarda apenas adendos específicos do Claude Code — edite AQUI, nunca duplique lá.

## O que é este repo

Marketplace **público** de plugins do Claude Code (`Caio-MOR/plugins`) com skills de **processo** (não de domínio de negócio), instaláveis em qualquer repositório Claude Code — não só no `template-cockpit`. Cada skill é um plugin independente, para poder ligar/desligar um sem afetar os outros.

Como o repo é público e instalado por pessoas fora do time (leigos, em VMs Windows e Linux), **nenhum arquivo pode conter rastro de uma máquina específica**: caminho `/Users/...`, `/private/tmp/...`, `.DS_Store`, ou comando que só existe no macOS. É a regra de portabilidade em `.claude/rules/portabilidade.md`. <!-- padrao-ouro:ignorar -->

## Estrutura de diretórios

| Procurando... | Vá para |
|---|---|
| Lista de plugins do marketplace (nome, versão, descrição) | `.claude-plugin/marketplace.json` |
| Um plugin específico (manifesto + skill) | `plugins/<nome>/` — `.claude-plugin/plugin.json` (manifesto) + `skills/<nome>/SKILL.md` (a skill) |
| Regras de processo do próprio repo (portabilidade, etc.) | `.claude/rules/` |
| Sub-agente verificador (autor ≠ verificador) | `.claude/agents/verificador.md` |
| Decisões e lições deste repo | `.specs/STATE.md`, `.specs/LESSONS.md` |
| Evals de comportamento de uma skill (formato oficial + runner de bolso) | `plugins/<nome>/evals/` (casos), `tools/eval_runner.py` (runner), `docs/evals.md` (grafo + prova de isolamento) |
| Validador do marketplace (JSON, frontmatter, rastro de máquina) | `tools/validar_plugins.py` |
| Teste do validador | `tests/test_validar_plugins.py` |
| CI (validação + varredura de segredos) | `.github/workflows/validar.yml`, `.github/workflows/gitleaks.yml` |
| Instruções para agentes e porta de entrada humana | `AGENTS.md` (fonte única), `CLAUDE.md` (importa este + adendos), `README.md` (humanos) |

## Como adicionar um plugin novo

1. Criar `plugins/<nome>/.claude-plugin/plugin.json` (`name`, `description`, `version`, `author`) e `plugins/<nome>/skills/<nome>/SKILL.md` com frontmatter (`name` igual ao nome da pasta, `description`, `formato:` — ver `.claude/rules/portabilidade.md`).
2. Registrar a entrada em `.claude-plugin/marketplace.json` (`name`, `source`, `description`, `version` — igual ao `plugin.json`).
3. Se a skill for de terceiro, preservar frontmatter e licença originais; documentar autoria/licença no `README.md`.
4. Rodar `python tools/validar_plugins.py` e `python -m pytest -q` antes de commitar.

## Como testar

- `python tools/validar_plugins.py` — valida JSON do marketplace e de cada plugin, consistência name/version, frontmatter de cada `SKILL.md` e ausência de caminho de máquina (`/Users/`, `/home/`) em arquivo versionado.
- `python -m pytest -q` — suíte em `tests/`.
- Ambos rodam no CI em todo push e PR (`.github/workflows/validar.yml`, matriz ubuntu sempre + windows em PR) e a varredura de segredos roda em `.github/workflows/gitleaks.yml`.
- **Evals de comportamento** (`plugins/<nome>/evals/`, formato oficial de `claude plugin eval`): `python tools/eval_runner.py --all` roda a suíte de disparo via `claude -p` (login de subscription, não API). Gate **local**, não CI — sem credencial no CI. `tests/test_evals_estrutura.py` (estrutura, sem LLM) e `tests/test_eval_runner.py` (parser + graders com fixtures sintéticas) esses sim rodam no CI. **Mudou a `description` de uma skill → rode `python tools/eval_runner.py --plugin <nome>` antes da PR e cole o placar** (comando + data) — é o que prova que a description ainda dispara certo. Detalhe, grafo e a prova de isolamento em `docs/evals.md`.

## Hard Rules (disciplina inegociável)

1. **Pense antes de codar.** Em caso de ambiguidade, pergunte em vez de assumir.
2. **Simplicidade primeiro.** Resolva exatamente o que foi pedido.
3. **Mudanças cirúrgicas.** Nunca modifique arquivos não mencionados na tarefa; nunca altere o corpo de uma skill de terceiro sem necessidade.
4. **Guiado por objetivo + verificação.** Rode o validador e a suíte antes de declarar pronto; cole a evidência.

## Regras globais

- Fale em **português brasileiro** por padrão.
- **Portabilidade Windows/Linux/Mac é regra absoluta** — `.claude/rules/portabilidade.md`.
- Licenças de terceiros (`tlc-spec-driven`: CC-BY-4.0; `systematic-debugging`: herdada do superpowers, MIT) ficam preservadas no frontmatter de cada skill e documentadas no `README.md`.
- O marketplace não é pinado por commit no exemplo de instalação: quem protege o repo contra mudança indevida é o dono (branch protection), não o consumidor congelando uma revisão.

## Resumo

Este repo distribui skills de processo para quem usa Claude Code, incluindo gente fora do time e fora do Mac. Leia as regras, valide antes de publicar, preserve as licenças de terceiros.
