# Concept Card: Parser & Binding

**Card ID:** CC-003  
**Type:** Core Concept  
**Repository:** python-dotenv  

## Identity

The parser is a regex-based tokenizer that converts `.env` file content into structured `Binding` objects. It handles quotes (single/double), escape sequences, comments, and multiline values. A `Binding` is a NamedTuple containing the parsed key, optional value, and source location metadata.

## Is / Is Not

| Is | Is Not |
|----|--------|
| Regex-based tokenizer | AST parser |
| Line-by-line processor | Full syntax tree |
| Error-tolerant (marks invalid lines) | Strict validator |
| Streaming (iterator interface) | In-memory load-all |

## Key Attributes

| Component | Purpose |
|-----------|---------|
| `Reader` class | Character stream with mark/peek |
| `Binding` NamedTuple | `key`, `value`, `original`, `error` |
| `parse_stream()` | Main entry point, yields Bindings |
| Escape sequences | `\\`, `\'`, `\"`, `\n`, `\t`, etc. |

## Boundaries

- **Valid keys:** Unquoted (`FOO`), single-quoted (`'FOO'`)
- **Valid values:** Unquoted, single-quoted, double-quoted
- **Comments:** `#` preceded by whitespace
- **Multiline:** Only in quoted values

## Evidence

```python
# src/dotenv/parser.py:36-45
class Binding(NamedTuple):
    key: Optional[str]
    value: Optional[str]
    original: Original  # (string, line_number)
    error: bool  # True if line is malformed

# src/dotenv/parser.py:180
def parse_stream(stream: IO[str]) -> Iterator[Binding]:
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)
```
