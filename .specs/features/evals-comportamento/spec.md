# Evals de comportamento das skills — Specification

Fatia do plano "nota 10 do template e plugins" (Cakopit, memória `projeto-template-plugins-nota-95`). Decisão registrada em 03/09/2026: "evals de comportamento (`claude plugin eval`) ficam para spec própria, depois". Esta é a spec.

## Problema

O repo `plugins` mede 10,0 no auditor do padrão ouro, mas tudo que o gate confere é **forma** (frontmatter, `formato:`, JSON, caminhos). Nada prova que uma skill **dispara quando deve e fica quieta quando não deve**. A `description` de cada skill é a única coisa que o modelo lê para decidir invocá-la, e hoje ela nunca foi testada contra pedidos reais. O mesmo vale para o `template-cockpit`, que ensina a criar skills sem ensinar a testá-las.

## Fato que define o desenho

`claude plugin eval` é **early access habilitado por organização**; na instalação local (Claude Code 2.1.191) o subcomando não existe. O formato oficial da suíte, porém, é conhecido: pasta `evals/` na raiz do plugin, um diretório por caso com `prompt.md` (frontmatter `name`, `tags`, `runs`, `max_turns`, `timeout_seconds` + corpo = prompt) e `graders/<nome>.md` (frontmatter `type: tool_used | regex | file_exists | llm`, campos do grader; corpo = justificativa). Caso negativo = grader `tool_used` com `min: 0, max: 0`. Idioma "skill disparou" = `tool: Skill`, `input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill>"'`.

**Decisão de desenho:** escrever os casos **no formato oficial**, para rodarem sem alteração no dia em que a flag abrir, e ter um **runner de bolso** (`tools/eval_runner.py`, stdlib pura) que lê esse mesmo formato e executa via `claude -p` com login de subscription (regra da casa: automação LLM via subscription, não API). O runner cobre só o subconjunto de graders que usamos (`tool_used`, `regex`, `file_exists`); `llm` e `baseline` ficam para a ferramenta oficial.

## Objetivos

- [ ] Cada skill dos 3 plugins (`os-audit`, `systematic-debugging`, `tlc-spec-driven`) tem suíte em `plugins/<plugin>/evals/` com **≥ 3 casos positivos e ≥ 3 negativos**.
- [ ] `tools/eval_runner.py` roda a suíte de um plugin (ou de todos) com `claude -p`, N runs por caso, e devolve placar por caso, exit code 0/1 e JSON de resultado com o mesmo espírito do `aggregate-result.json` oficial (`cases[].runs[].graders[]`, `aggregates`).
- [ ] Gate **determinístico** no CI (`tests/test_evals_estrutura.py`): estrutura, frontmatter e mínimo de casos por skill; roda sem LLM. A execução com LLM é gate **local** (antes de mergear mudança em `description`), não CI, porque o CI não tem credencial de subscription e não se paga API para isso.
- [ ] `template-cockpit` recebe o mesmo runner, um caso positivo e um negativo para `_exemplo-skill` e o teste estrutural, para que todo repo instanciado nasça com o hábito.
- [ ] Rodada real executada: suíte dos 3 plugins rodada com 3 runs por caso; resultado colado na PR. Se uma `description` reprovar, ajustá-la (teto: 3 rodadas de ajuste por skill) e registrar o antes/depois.

## Fora de escopo

| Item | Motivo |
|---|---|
| Cakopit (repo `Cloud Cowork ptbr`) | Decisão do Caio 03/09: melhorias chegam ao Cakopit só depois dos dois repos |
| Mudar `PADRAO.md`/auditor para exigir evals (PO-S04) | Norma vive no Cakopit; decisão do Caio pendente (ver Perguntas) |
| Graders `llm`/`baseline`, ablation, mocks de MCP | Só a ferramenta oficial; o runner de bolso não os imita |
| Testar o **conteúdo** do que a skill faz (ex.: o os-audit gerou relatório correto) | Esta fatia testa **disparo**; comportamento interno é fatia própria, por skill |
| Rodar eval no CI | Sem credencial; ver Objetivos |

## Requisitos (EARS)

**Formato dos casos**
- R1. Cada caso vive em `plugins/<plugin>/evals/<case>/` com `prompt.md` e ≥ 1 arquivo em `graders/`. Frontmatter de `prompt.md`: `name` (= nome da pasta), `tags` (lista, contendo `positivo` ou `negativo`), `runs: 3`, `max_turns: 3`, `timeout_seconds: 180`.
- R2. Grader de disparo: `type: tool_used`, `tool: Skill`, `input_match` com a regex oficial para o nome da skill; positivo `min: 1`; negativo `min: 0, max: 0`.
- R3. Prompts em PT-BR, sem dado concreto da MOR (regra do padrão ouro: estrutura, não conteúdo). Cada skill tem obrigatoriamente: (a) 1 positivo com a frase-gatilho literal da `description`; (b) 2 positivos parafraseados, sem nenhuma palavra-chave literal da `description`; (c) 1 negativo "vizinho" (tema parecido que NÃO é a skill — ex.: para `os-audit`, "revise a segurança deste código"; para `systematic-debugging`, "explica o que é um stack trace"; para `tlc-spec-driven`, "resume o que é spec-driven development"); (d) 1 negativo cruzado (prompt que deve disparar **outra** skill do marketplace e não esta); (e) 1 negativo neutro (pergunta genérica).
- R4. Nenhum caso pode depender de arquivo pré-existente no cwd (o runner roda em diretório temporário vazio).

**Runner**
- R5. `python tools/eval_runner.py [--plugin <nome>|--all] [--runs N] [--case glob] [--json <arquivo>] [--threshold 0..1]`. Default: `--all`, runs do frontmatter, threshold 1.0 (igual ao default oficial).
- R6. Para cada run: `claude -p "<prompt>" --output-format stream-json --verbose --max-turns <max_turns> --plugin-dir <caminho do plugin> --setting-sources project --permission-mode dontAsk`, cwd = diretório temporário vazio, timeout = `timeout_seconds`. Isolamento é requisito: skills e plugins do usuário (o Cakopit tem skills com os mesmos nomes) **não podem** estar carregados. Prova exigida (T4).
- R7. Grader `tool_used`: contar blocos `tool_use` com `name == "Skill"` cuja entrada serializada casa `input_match`; comparar com `min`/`max`. Grader `regex`: sobre a última mensagem do assistente. Grader `file_exists`: glob no cwd temporário após o run.
- R8. Saída: tabela por caso (`caso | tag | runs ok / runs | veredito`) no stdout; JSON opcional; exit 0 se todo caso ≥ threshold, 1 se algum abaixo, 2 se o `claude` falhou de autenticação ou não foi encontrado (mensagem clara: "faça login no Claude Code antes de rodar").
- R9. Freios (regra loop-engineering): teto de runs por caso = valor do frontmatter (nunca re-tentar além); timeout por run; se 3 casos consecutivos falharem por erro de infraestrutura (não por grader), abortar com exit 2 em vez de insistir.
- R10. Resultados em `evals/results/` **não versionados** (gitignore allowlist: liberar `evals/` e negar `evals/results/`).

**Gate determinístico (CI)**
- R11. `tests/test_evals_estrutura.py`: para cada plugin do marketplace, `evals/` existe; cada caso tem `prompt.md` com frontmatter válido e `name` = pasta; ≥ 3 positivos e ≥ 3 negativos; todo grader `tool_used` tem regex compilável; `runs`, `max_turns`, `timeout_seconds` são inteiros positivos; nenhum prompt contém caminho de máquina (`/Users/`, `/home/`, `C:\`).
- R12. `tests/test_eval_runner.py`: testa o **parser de casos** e os **graders** com transcrições `stream-json` sintéticas (fixture em `tests/fixtures/`), sem chamar o `claude`. Inclui teste de mutação: um grader negativo com um `tool_use` de Skill na transcrição **reprova**; sem ele, aprova. Inclui teste do exit code 2 com `claude` ausente (PATH vazio).
- R13. Teste do runner e do gate rodam na matriz existente (`validar.yml`: ubuntu + windows). Portabilidade é regra absoluta do repo: nada de `sh`, caminhos POSIX ou `shell=True`.

**Documentação e grafo**
- R14. `AGENTS.md` do `plugins`: seção "Como testar" ganha a linha do runner e a regra "mudou `description` → roda `eval_runner` antes da PR e cola o placar". `README.md`: seção "Evals" curta com o formato e o aviso de early access.
- R15. Grafo Mermaid do runner (formato: **loop com teto**, casos × runs, dentro de uma cadeia parse → executa → avalia → relata) em `docs/evals.md` do repo `plugins` (criar `docs/` e liberar no gitignore), com o wait test na linha do formato.
- R16. `.specs/STATE.md` do `plugins` recebe **AD-002**: eval no formato oficial + runner de bolso; execução é gate local, não CI; motivo (early access + credencial).

**Template-cockpit**
- R17. Copiar `tools/eval_runner.py` e `tests/test_eval_runner.py` (adaptando caminhos: skills em `.claude/skills/`, sem plugin; o runner aceita `--skills-dir` além de `--plugin-dir`, e nesse modo usa `--setting-sources project` com cwd = raiz do repo e um `.claude/skills` contendo só a skill sob teste, copiada para o temporário). Criar `evals/_exemplo-skill/` com 1 positivo e 1 negativo. `tests/test_evals_estrutura.py` no template exige ≥ 1 positivo e ≥ 1 negativo por skill (o template é modelo, não produção). Liberar `evals/` no gitignore do template; `docs/padrao-ouro/PADRAO.md` **não** é alterado.
- R18. O `test_criacao_nova.py` do template passa a exigir que skill nova venha com pasta `evals/<skill>/` contendo ≥ 1 positivo e ≥ 1 negativo (o gate de criação nova já existe; é só uma porta a mais, e a lista de isentos legados fica vazia porque a única skill é o exemplo).

## Critério de pronto (verificável por comando)

1. `python -m pytest -q` verde nos dois repos, local (Windows) e no CI (ubuntu + windows).
2. `python tools/validar_plugins.py .` verde no `plugins`; `python tools/padrao_ouro_audit.py --tipo cockpit --template .` continua 10,0 no template.
3. `python tools/eval_runner.py --all --json evals-resultado.json` no `plugins`: exit 0, ≥ 18 casos executados (3 skills × 6), placar colado na descrição da PR **com o comando e a data**.
4. Mutação viva: trocar temporariamente a `description` do `os-audit` por "Use quando pedirem a capital de um país" e rodar o runner → os positivos do `os-audit` reprovam (prova de que o eval mede a description, não a sorte). Reverter. Colar a saída na PR.
5. Duas PRs abertas (rulesets exigem PR): `Caio-MOR/plugins` `feat/evals-comportamento` e `Caio-MOR/template-cockpit` `feat/evals-comportamento`, ambas com CI verde, sem merge (merge é do Caio).

## Perguntas ao Caio (não bloqueiam; assumido o default)

| Pergunta | Default assumido |
|---|---|
| `PADRAO.md` ganha exigência PO-S04 "toda skill tem eval de disparo (≥1 positivo, ≥1 negativo)" e o auditor passa a medir? Mexe no Cakopit. | **Não nesta fatia.** Registrar como próxima. |
| Threshold 1.0 (todos os runs) ou 2/3 para positivos? | 1.0, igual ao default oficial. Flakiness é sintoma de `description` ambígua, que é justamente o que queremos ver. |
| Rodar eval também numa rotina agendada (semanal)? | Não. Gate local antes de PR basta; rotina só se a frota de skills crescer. |
