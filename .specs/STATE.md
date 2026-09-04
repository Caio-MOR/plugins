# STATE

Log de decisões do repo (append-only) e snapshot de handoff. Uma decisão por item, com data e motivo — o porquê é o que a próxima sessão não consegue reconstruir sozinha.

## Decisions

<!-- Formato de cada entrada (uma por decisão, mais recente por último):
- **AD-001 (AAAA-MM-DD):** o que foi decidido, em uma frase; o motivo em outra.
  Quem decidiu (dono do repo em chat, agente por regra X) e o que fica em aberto.
-->

- **AD-001 (2026-09-03):** proteger o repo em vez de pinar o marketplace por commit. O exemplo de instalação (`extraKnownMarketplaces` apontando para `Caio-MOR/plugins`) não fixa SHA/tag — quem defende o repo contra mudança indevida é o dono, via branch protection e revisão de PR, não o consumidor congelando uma revisão que nunca recebe correção.
  Decisão do Caio (dono do repo), registrada durante o trabalho de padrão ouro. Em aberto: nenhum.

## Handoff snapshot
