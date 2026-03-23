---
card_type: community_rule
card_id: DR-101
repo: python-dotenv
type: UNSAID_GOTCHA
title: load_dotenv Returns True Even If .env Not Found
---

# Community Gotcha: load_dotenv Return Value

**Card ID:** DR-101  
**Type:** Unsaid Gotcha  
**Repository:** python-dotenv  

## The Gotcha

`load_dotenv()` returns `True` even when the `.env` file is not found. This can mislead users into thinking loading succeeded.

```python
result = load_dotenv()  # Returns True even if .env doesn't exist!
```

## Context

From Issue #321 on GitHub: Users expect `load_dotenv()` to return `False` when `.env` is missing, but it returns `True` because it successfully loads zero variables (which is considered a success).

## Workaround

Use `verbose=True` to see warnings, or check for file existence manually:

```python
from pathlib import Path
if Path(".env").exists():
    load_dotenv()
```

## Confidence

**VALIDATED** — Confirmed by multiple Stack Overflow and GitHub issues.

## Sources

- GitHub Issue #321: https://github.com/theskumar/python-dotenv/issues/321
- Stack Overflow: https://stackoverflow.com/questions/64734118
