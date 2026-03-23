---
card_type: decision_rule
card_id: DR-002
repo: python-dotenv
type: CORE_BEHAVIOR
title: find_dotenv Search Behavior
---

# Decision Rule: find_dotenv Search Behavior

**Card ID:** DR-002  
**Type:** Core Behavior  
**Repository:** python-dotenv  

## Rule

```yaml
IF: Running in interactive environment (REPL/IPython)
THEN: Search from current working directory

IF: Running as script (has __file__)
THEN: Search from script's directory upward

IF: Running in debugger
THEN: Search from current working directory (regardless of __file__)
```

## Context

`find_dotenv()` automatically locates `.env` files by searching upward from the current context. The search starting point depends on how the code is executed.

## Do

- Use explicit `dotenv_path=` when location is predictable
- Use `usecwd=True` to force CWD-based search
- Place `.env` in project root for standard behavior

## Don't

- Don't assume `.env` is always found in CWD
- Don't rely on auto-discovery in imported library code
- Don't use in production without explicit paths

## Evidence

```python
# src/dotenv/main.py:188-210
def find_dotenv(
    filename: Union[str, "os.PathLike[str]"] = ".env",
    usecwd: bool = False,
    raise_error_if_not_found: bool = False,
    load_if_dotenv: bool = False,
) -> str:
    if _is_interactive() or _is_debugger() or usecwd:
        # Search from cwd
    else:
        # Search from __file__ directory
```

## Confidence

**HIGH** — Core documented behavior.
