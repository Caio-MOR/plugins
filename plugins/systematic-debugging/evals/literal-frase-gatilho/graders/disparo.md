---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?systematic-debugging"'
min: 1
---

Caso positivo: o prompt descreve, com ou sem a frase-gatilho literal, uma
situação coberta pela `description` da skill `systematic-debugging`. Espera-se pelo menos
um `tool_use` de `Skill` cuja entrada nomeie `systematic-debugging` (com ou sem prefixo de
plugin).
