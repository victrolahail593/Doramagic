---
card_type: community_rule
card_id: DR-103
repo: python-dotenv
type: UNSAID_BEST_PRACTICE
title: Don't Use load_dotenv in Library Code
---

# Community Best Practice: Library Code Should Not Call load_dotenv

**Card ID:** DR-103  
**Type:** Unsaid Best Practice  
**Repository:** python-dotenv  

## The Gotcha

Libraries/packages should not call `load_dotenv()` because it modifies global state (`os.environ`) and can interfere with other parts of the application or other libraries.

## Context

`load_dotenv()` modifies the global process environment. If a library does this:
- It may override user-provided environment variables
- It may conflict with other libraries doing the same
- It makes behavior non-deterministic

## Best Practice

**For libraries:**
- Use `dotenv_values()` instead — returns dict without modifying globals
- Document required environment variables
- Let the application handle loading

**For applications:**
- Call `load_dotenv()` once at startup
- Use explicit paths: `load_dotenv(dotenv_path=...)`

## Example

```python
# ❌ Library code (bad)
def my_library_init():
    load_dotenv()  # Modifies global state!

# ✅ Library code (good)
def my_library_init():
    config = dotenv_values()  # Read-only
    required_vars = ["API_KEY"]
    # Validate and use config
```

## Confidence

**VALIDATED** — Widely accepted best practice in Python community.

## Sources

- Python-dotenv README best practices
- 12-factor app methodology
