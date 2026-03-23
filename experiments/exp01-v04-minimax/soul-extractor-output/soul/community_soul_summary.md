# Community Soul Summary

## What the Community Knows (That Docs Don't Tell You)

### Top Gotchas

| ID | Gotcha | Impact | Workaround |
|----|--------|--------|------------|
| DR-101 | `load_dotenv()` returns True even if .env missing | Silent failures | Check file existence manually |
| DR-102 | Doesn't find .env in venv/project dir | Variables not loaded | Use explicit `dotenv_path=` |
| DR-103 | Libraries shouldn't call load_dotenv | Global state pollution | Use `dotenv_values()` instead |

### Common Mistakes

1. **Assuming .env always wins** — `override=False` by default means existing env vars take precedence
2. **Import confusion** — Package is `python-dotenv`, import is `dotenv`
3. **Path confusion** — Relative paths are relative to script, not CWD (in non-interactive mode)
4. **Silent failures** — Syntax errors in .env are logged but don't raise exceptions

### Best Practices (Community-Validated)

1. **Explicit paths** — Always use `dotenv_path=` in production
2. **Override in tests** — Use `override=True` for reproducible tests
3. **Validate on load** — Check return value and use `verbose=True` during development
4. **One-time loading** — Call `load_dotenv()` once at application startup
5. **Don't commit .env** — Add to `.gitignore`, use `.env.example`

### Version-Specific Notes

- **v1.0+**: Dropped Python 3.7 support
- **v0.18.0+**: Single quotes used by default for `set_key`
- **v0.15.0+**: Returns False when no variables set (improved)
- **v0.10.0+**: UTF-8 support in unquoted values

### Related Tools in Ecosystem

- **environs** — Type-safe env parsing with validation
- **dynaconf** — Multi-format config with layers
- **Honcho** — Procfile-based development
- **django-environ** — Django-specific wrapper

## Summary

python-dotenv is simple but has subtle behaviors around:
- File discovery (venv, CWD, script location)
- Override precedence
- Return values and silent failures

**Pro tip:** In production, always use explicit paths and validate loading success.
