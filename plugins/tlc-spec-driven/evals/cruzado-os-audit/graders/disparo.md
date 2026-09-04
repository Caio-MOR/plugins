---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?tlc-spec-driven"'
min: 0
max: 0
---

Caso negativo: o prompt não deve disparar a skill `tlc-spec-driven`. Zero `tool_use`
de `Skill` cuja entrada nomeie `tlc-spec-driven` em todos os runs.
