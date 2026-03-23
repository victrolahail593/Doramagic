# Eagle Eye Identity

## Project Identity

**Name:** python-dotenv  
**Version:** 1.2.2  
**Author:** Saurabh Kumar  
**License:** BSD-3-Clause  
**Python Version:** >=3.10  
**Purpose:** Reads key-value pairs from a `.env` file and sets them as environment variables, following 12-factor app principles.

## Core Concepts

| Concept | Definition | Evidence |
|---------|------------|----------|
| `.env` file | A text file containing key-value pairs for environment variables | `src/dotenv/main.py` |
| Variable expansion | POSIX-style variable interpolation like `${DOMAIN}` or `$VAR` | `src/dotenv/variables.py` |
| DotEnv class | Core class that parses .env files and manages key-value bindings | `src/dotenv/main.py:70` |
| Parser | Regex-based tokenizer that handles quotes, escapes, comments | `src/dotenv/parser.py` |
| Binding | NamedTuple representing a parsed key-value line with metadata | `src/dotenv/parser.py:36` |
| find_dotenv() | Searches upward from current directory to find .env file | `src/dotenv/main.py:188` |
| load_dotenv() | Loads .env into os.environ, optionally overriding existing vars | `src/dotenv/main.py:216` |
| dotenv_values() | Returns dict of values without modifying environment | `src/dotenv/main.py:250` |
| CLI commands | set, get, unset, list, run - manipulate .env from command line | `src/dotenv/cli.py` |
| IPython magic | `%dotenv` magic for loading .env in IPython/Jupyter | `src/dotenv/ipython.py` |

## Key Files

- **Entry point:** `src/dotenv/__init__.py`
- **CLI entry:** `src/dotenv/__main__.py` → `cli.py`
- **Main logic:** `src/dotenv/main.py` (~400 lines)
- **Parser:** `src/dotenv/parser.py` (~200 lines)
- **Variables:** `src/dotenv/variables.py` (~100 lines)
