# caio-mor — marketplace de plugins do Claude Code

Marketplace privado com skills de **processo** (não de domínio de negócio) para uso em qualquer repo criado a partir do `template-cockpit` ou de outro projeto Claude Code. Cada skill é um plugin independente, para poder ligar/desligar um sem afetar os outros.

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
