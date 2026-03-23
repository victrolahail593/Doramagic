# Concept Card: DotEnv Class

**Card ID:** CC-001  
**Type:** Core Concept  
**Repository:** python-dotenv  

## Identity

The `DotEnv` class is the central engine that parses `.env` files and provides a Python interface for accessing key-value bindings. It encapsulates all parsing logic and exposes methods for iterating over bindings, converting to dict, and setting as environment variables.

## Is / Is Not

| Is | Is Not |
|----|--------|
| A parser wrapper | A file reader directly |
| State-bearing (stores parsed bindings) | Stateless utility |
| Iterator (yields Binding tuples) | Dict subclass |
| Configurable (encoding, interpolate) | Fixed configuration |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `path` | StrPath | Path to .env file |
| `stream` | Optional[IO[str]] | Alternative stream input |
| `encoding` | str | File encoding (default: utf-8) |
| `interpolate` | bool | Enable variable expansion |

## Boundaries

- **Input:** `.env` file path or `StringIO` stream
- **Output:** Iterator of `(key, value)` tuples, or dict
- **Side effects:** Can set `os.environ` via `set_as_environment_variables()`

## Evidence

```python
# src/dotenv/main.py:70-90
class DotEnv:
    @contextmanager
    def _get_stream(self) -> Iterator[IO[str]]:
        # Opens file or uses provided stream
        
    def parse(self) -> Iterator[Tuple[str, Optional[str]]]:
        # Yields key-value pairs
        
    def dict(self) -> Dict[str, Optional[str]]:
        # Returns all bindings as dict
```
