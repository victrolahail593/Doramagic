---
card_type: community_rule
card_id: DR-102
repo: python-dotenv
type: UNSAID_GOTCHA
title: find_dotenv Doesn't Find .env in Current Directory in venv
---

# Community Gotcha: Virtual Environment Path Issue

**Card ID:** DR-102  
**Type:** Unsaid Gotcha  
**Repository:** python-dotenv  

## The Gotcha

When running from within a virtual environment, `find_dotenv()` may search from the venv's site-packages directory instead of the current working directory, failing to find `.env`.

## Context

From Issue #108 (2018): If `load_dotenv()` is called from within a virtual environment, the search path starts from `<venv>/lib/python3.x/site-packages/dotenv/` rather than the project directory.

## Workaround

1. Use explicit path:
   ```python
   load_dotenv(dotenv_path=".env")
   ```

2. Use `usecwd=True`:
   ```python
   find_dotenv(usecwd=True)
   ```

3. Use absolute path:
   ```python
   load_dotenv(dotenv_path=Path(__file__).parent / ".env")
   ```

## Confidence

**VALIDATED** — Multiple reports, common in Django/Flask projects.

## Sources

- GitHub Issue #108: https://github.com/theskumar/python-dotenv/issues/108
