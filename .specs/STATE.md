# STATE

Log de decisões do repo (append-only) e snapshot de handoff. Uma decisão por item, com data e motivo — o porquê é o que a próxima sessão não consegue reconstruir sozinha.

## Decisions

<!-- Formato de cada entrada (uma por decisão, mais recente por último):
- **AD-001 (AAAA-MM-DD):** o que foi decidido, em uma frase; o motivo em outra.
  Quem decidiu (dono do repo em chat, agente por regra X) e o que fica em aberto.
-->

- **AD-001 (2026-09-03):** proteger o repo em vez de pinar o marketplace por commit. O exemplo de instalação (`extraKnownMarketplaces` apontando para `Caio-MOR/plugins`) não fixa SHA/tag — quem defende o repo contra mudança indevida é o dono, via branch protection e revisão de PR, não o consumidor congelando uma revisão que nunca recebe correção.
  Decisão do Caio (dono do repo), registrada durante o trabalho de padrão ouro. Em aberto: nenhum.

- **AD-002 (2026-09-03):** eval de comportamento no formato oficial de `claude plugin eval` + um runner de bolso (`tools/eval_runner.py`), em vez de esperar a flag de early access abrir. Motivo: a flag é habilitada por organização e não existe nesta instalação (2.1.191), mas o formato da suíte (`prompt.md` + `graders/`) já é conhecido e documentado — escrever os casos nele já paga o dia em que a flag abrir. A execução com LLM é gate **local** (antes de PR que mude uma `description`), nunca CI: o CI não tem credencial de subscription e não se paga API para isso; o CI cobre só o gate estrutural determinístico (`tests/test_evals_estrutura.py`, sem LLM).
  Decisão do Caio, registrada na spec `evals-comportamento`. Em aberto: a prova de isolamento e a rodada real (T4/T7/T8) ficaram bloqueadas nesta sessão porque o `claude` CLI standalone não autentica quando invocado como subprocesso a partir do agente que fez este trabalho (`~/.claude/.credentials.json` desatualizado; a sessão do app não é a sessão do CLI) — detalhe e comandos para reproduzir em `docs/evals.md`. Pendência do Caio: `claude /login` num terminal interativo antes da próxima rodada.

## Handoff snapshot
