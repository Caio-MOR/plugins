---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?os-audit"'
min: 1
---

Caso positivo: o prompt descreve, com ou sem a frase-gatilho literal, uma
situação coberta pela `description` da skill `os-audit`. Espera-se pelo menos
um `tool_use` de `Skill` cuja entrada nomeie `os-audit` (com ou sem prefixo de
plugin).
