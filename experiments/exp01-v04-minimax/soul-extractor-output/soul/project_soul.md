# Project Soul: python-dotenv

## Design Principles

1. **Minimalism** — Do one thing well: load .env files into environment variables
2. **12-Factor Compliance** — Configuration from environment, not code
3. **Non-invasive** — Default doesn't override existing env vars
4. **Error-tolerant** — Silently skips malformed lines rather than crashing
5. **Extensible** — Supports streams, custom paths, interpolation control

## Architecture in One Sentence

python-dotenv is a lightweight, regex-based `.env` parser that provides both imperative loading (`load_dotenv()`) and declarative reading (`dotenv_values()`), with CLI and IPython integrations, while carefully avoiding global state pollution in library contexts.

## Card Index

### Concept Cards
| ID | Title | File |
|----|-------|------|
| CC-001 | DotEnv Class | concepts/CC-001-dotenv-class.md |
| CC-002 | Variable Expansion | concepts/CC-002-variable-expansion.md |
| CC-003 | Parser & Binding | concepts/CC-003-parser-binding.md |

### Workflow Cards
| ID | Title | File |
|----|-------|------|
| WF-001 | Loading .env File | workflows/WF-001-load-dotenv.md |
| WF-002 | Variable Expansion Resolution | workflows/WF-002-variable-expansion.md |

### Core Decision Rules
| ID | Title | File |
|----|-------|------|
| DR-001 | Variable Override Precedence | rules/DR-001-override-precedence.md |
| DR-002 | find_dotenv Search Behavior | rules/DR-002-find-dotenv.md |

### Community Rules (Gotchas)
| ID | Title | File |
|----|-------|------|
| DR-101 | load_dotenv Return Value | rules/DR-101-load-dotenv-return-value.md |
| DR-102 | Virtual Environment Path Issue | rules/DR-102-venv-path.md |
| DR-103 | Library Code Best Practice | rules/DR-103-library-code.md |

## Key Insights

### What Makes This Project Special
- **Small footprint** (~3200 lines of Python, no dependencies beyond Click for CLI)
- **Battle-tested** — Used by Flask, Django, and thousands of projects
- **Well-maintained** — Active since 2014, regular releases

### Core Value
The genius is in the simplicity: it's not trying to be a config management system, just a clean bridge between `.env` files and `os.environ`.

### Learning for Similar Projects
1. **Regex > AST** — For simple formats, regex is sufficient and lighter
2. **Iterator over list** — `parse_stream()` yields, doesn't collect
3. **Graceful degradation** — Silent failure on missing files, warnings on parse errors
4. **Clear boundaries** — Core library doesn't touch globals; CLI does

---

**Generated:** 2026-03-09  
**Repository:** https://github.com/theskumar/python-dotenv  
**Version Analyzed:** 1.2.2  
**Total Lines:** 3,201 Python
