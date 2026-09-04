---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?os-audit"'
min: 0
max: 0
---

Caso negativo: o prompt não deve disparar a skill `os-audit`. Zero `tool_use`
de `Skill` cuja entrada nomeie `os-audit` em todos os runs.
