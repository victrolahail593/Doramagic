---
card_type: decision_rule
card_id: DR-001
repo: python-dotenv
type: CORE_BEHAVIOR
title: Variable Override Precedence
---

# Decision Rule: Variable Override Precedence

**Card ID:** DR-001  
**Type:** Core Behavior  
**Repository:** python-dotenv  

## Rule

```yaml
IF: load_dotenv(override=False)
THEN: os.environ values take precedence over .env file values

IF: load_dotenv(override=True)  
THEN: .env file values take precedence over os.environ values
```

## Context

When loading `.env` files, there are two sources of environment variables:
1. Existing `os.environ` (from parent shell or previous setup)
2. Values from the `.env` file

The `override` parameter controls which source wins.

## Do

- Use `override=False` (default) for development to respect existing shell variables
- Use `override=True` in tests to ensure reproducible environment
- Use `dotenv_values()` + dict merge for complex precedence rules

## Don't

- Don't assume .env values always win — they don't by default
- Don't use `load_dotenv()` in library code — it modifies global state
- Don't rely on order of multiple `load_dotenv()` calls with different files

## Applies To

- `load_dotenv()` — main.py:216
- `dotenv_values()` — main.py:250

## Confidence

**HIGH** — This is documented behavior with clear API.

## Evidence

```python
# src/dotenv/main.py:216
def load_dotenv(
    dotenv_path: Optional[StrPath] = None,
    stream: Optional[IO[str]] = None,
    verbose: bool = False,
    override: bool = False,  # <-- Controls precedence
    ...
):
```
