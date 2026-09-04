# caio-mor — marketplace de plugins do Claude Code

Marketplace **público** (`gh repo view Caio-MOR/plugins --json visibility` confirma) com skills de **processo** (não de domínio de negócio) para uso em qualquer repo criado a partir do `template-cockpit` ou de outro projeto Claude Code — inclusive por gente fora do time, em VM Windows ou Linux. Cada skill é um plugin independente, para poder ligar/desligar um sem afetar os outros.

## Como rodar (validar localmente)

Só biblioteca padrão do Python 3.12+; roda em Windows, Linux e Mac.

```bash
python tools/validar_plugins.py   # JSON do marketplace/plugins, frontmatter das SKILL.md, rastro de máquina
python -m pytest -q               # suíte do validador
```

## Evals

Cada plugin tem uma suíte de disparo em `plugins/<nome>/evals/` no **formato oficial**
de `claude plugin eval` (`prompt.md` + `graders/`) — hoje **early access habilitado
por organização**, então o subcomando ainda não roda nesta instalação. Enquanto isso,
`tools/eval_runner.py` (stdlib + PyYAML) lê o mesmo formato e executa via `claude -p`:

```bash
python tools/eval_runner.py --all                      # todos os plugins
python tools/eval_runner.py --plugin os-audit           # um só
python tools/eval_runner.py --all --json resultado.json # placar + JSON
```

Exit 0 = todo caso disparou (ou não disparou) como esperado; 1 = alguma `description`
precisa de ajuste; 2 = `claude` não encontrado ou sem login. Detalhe do formato, grafo
do runner e a prova de isolamento (o CLI não roda skills do usuário nem de outro
plugin) em `docs/evals.md`.

Instalar num projeto Claude Code (ver "Como registrar" e "Como instalar" abaixo):

```
claude plugin marketplace add Caio-MOR/plugins
claude plugin install tlc-spec-driven@caio-mor
```

## Plugins

| Plugin | O que faz | Origem / licença |
|---|---|---|
| `tlc-spec-driven` | Planejamento e implementação de features guiado por spec (Specify → Design → Tasks → Execute), com gates deterministicos em Python e Verificador independente (autor ≠ verificador). | Terceiro: Felipe Rodrigues (github.com/felipfr), **CC-BY-4.0** |
| `systematic-debugging` | Depuração sistemática — causa-raiz obrigatória antes de qualquer correção. | Herdada do plugin **superpowers** (obra), **MIT** |
| `os-audit` | Auditoria read-only de drift/desatualização/organização de um projeto Claude Code (AIOS): índices desatualizados, roteamento quebrado, pastas duplicadas/inchadas. | Caio Kohn |

## Como registrar num projeto

No `.claude/settings.json` do repo:

```json
{
  "extraKnownMarketplaces": {
    "caio-mor": {
      "source": {
        "source": "github",
        "repo": "Caio-MOR/plugins"
      }
    }
  },
  "enabledPlugins": {
    "tlc-spec-driven@caio-mor": true,
    "systematic-debugging@caio-mor": true,
    "os-audit@caio-mor": true
  }
}
```

Registrar no `settings.json` **não instala** o plugin sozinho — é preciso instalar explicitamente (ver abaixo).

## Como instalar

```bash
claude plugin marketplace add Caio-MOR/plugins
claude plugin install tlc-spec-driven@caio-mor
claude plugin install systematic-debugging@caio-mor
claude plugin install os-audit@caio-mor
claude plugin list
```

## Como atualizar

```bash
claude plugin update tlc-spec-driven@caio-mor
# ou todos:
claude plugin update
```

## Como publicar uma versão nova de um plugin

1. Editar os arquivos da skill dentro de `plugins/<nome>/skills/<nome>/`.
2. Bump de `version` em **dois lugares**: `plugins/<nome>/.claude-plugin/plugin.json` e na entrada correspondente de `.claude-plugin/marketplace.json` (raiz).
3. `claude plugin validate .` na raiz e `claude plugin validate plugins/<nome>` no plugin alterado.
4. Commit + push. Quem já tem o plugin instalado atualiza com `claude plugin update`.

## Créditos e licenças de terceiros

- **tlc-spec-driven** — autoria de Felipe Rodrigues (github.com/felipfr), distribuída sob **CC-BY-4.0**. Frontmatter e licença preservados na cópia deste marketplace.
- **systematic-debugging** — herdada do plugin **superpowers** (obra coletiva), distribuída sob **MIT**.

---

Criado por Caio Kohn
