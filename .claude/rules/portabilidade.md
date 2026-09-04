# Portabilidade Windows/Linux/Mac (regra absoluta)

Este marketplace é público e instalado por gente fora do time, em máquinas que o autor nunca viu — majoritariamente VMs Windows e Linux. Uma skill ou script que só roda no Mac de quem escreveu quebra silenciosamente em todo mundo.

## Regras

1. **Nenhum rastro de máquina versionado.** Proibido: caminho absoluto `/Users/...`, `/home/...`, `C:\Users\...`; `.DS_Store`; qualquer comando que só existe no macOS (`osascript`, `pbcopy`, `open` sem fallback). O validador (`tools/validar_plugins.py`) reprova `/Users/` e `/home/` em qualquer arquivo versionado.
2. **Scripts de skill em Python ou POSIX-mínimo.** Preferir Python (roda igual nos três SOs) a shell. Quando shell for inevitável, escrever para **Git Bash** (o bash que já vem com o Git para Windows) — nada de bashisms exclusivos de macOS/BSD (`sed -i ''`, `ggrep`, etc.). Um script `.sh` que só funciona com o bash do Homebrew não é portável; documentar a exceção no `SKILL.md` (ver a nota do `find-polluter.sh`).
3. **Toda `SKILL.md` declara `formato:` no frontmatter.** Mesma mecânica do `graph-engineering.md` do template-cockpit: `cadeia`, `diamante`, `branch`, `loop` ou `híbrido(...)`, com uma frase de justificativa quando não for óbvio. O validador reprova `SKILL.md` sem o campo.

## Por que aqui e não só no CI

O CI pega o que já foi commitado; esta regra existe para a decisão ser tomada **antes** de escrever a linha — é mais barato não introduzir o rastro do que caçá-lo depois no `git grep`.
