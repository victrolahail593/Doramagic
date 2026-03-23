# Concept Card: Variable Expansion

**Card ID:** CC-002  
**Type:** Core Concept  
**Repository:** python-dotenv  

## Identity

Variable expansion is the process of resolving POSIX-style variable references in `.env` values, such as `${DOMAIN}`, `$USER`, or `${PORT:-8080}`. It allows `.env` files to reference other variables, create derived values, and use default fallback values.

## Is / Is Not

| Is | Is Not |
|----|--------|
| POSIX-compatible expansion | Shell-specific syntax |
| Recursive (can chain) | Templating engine |
| Default value support `${VAR:-default}` | Conditional logic |
| Resolves at parse time | Runtime evaluation |

## Key Attributes

| Pattern | Example | Result |
|---------|---------|--------|
| `$VAR` | `FOO=$BAR` | Direct reference |
| `${VAR}` | `URL=${HOST}:${PORT}` | Braced reference |
| `${VAR:-default}` | `PORT=${PORT:-8080}` | Default fallback |
| `${VAR:+alternate}` | `DEBUG=${DEBUG:+true}` | Alternate value |

## Boundaries

- **Precedence:** .env file → environment → default → empty string
- **Override mode:** When `override=True`, .env values take precedence over existing env vars
- **No override mode:** Existing env vars take precedence over .env values

## Evidence

```python
# src/dotenv/variables.py:48-70
class Variable(Atom):
    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        default = self.default if self.default is not None else ""
        return env.get(self.name, default)
```
