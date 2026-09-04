---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?systematic-debugging"'
min: 0
max: 0
---

Caso negativo: o prompt não deve disparar a skill `systematic-debugging`. Zero `tool_use`
de `Skill` cuja entrada nomeie `systematic-debugging` em todos os runs.
