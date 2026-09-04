---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?tlc-spec-driven"'
min: 1
---

Caso positivo: o prompt descreve, com ou sem a frase-gatilho literal, uma
situação coberta pela `description` da skill `tlc-spec-driven`. Espera-se pelo menos
um `tool_use` de `Skill` cuja entrada nomeie `tlc-spec-driven` (com ou sem prefixo de
plugin).
