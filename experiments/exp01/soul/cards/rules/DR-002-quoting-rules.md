---
card_type: decision_rule_card
card_id: DR-002
repo: python-dotenv
type: DESIGN_DECISION
title: "Quoting Rules -- How Value Quoting Affects Parsing"
rule: |
  Three quoting modes exist for .env values, each with distinct escape and comment rules:
  1. Single-quoted ('...'): Only \\ and \' are escape sequences. No variable interpolation occurs at parse level (but interpolation happens later in resolve_variables if enabled). Preserves literal content.
  2. Double-quoted ("..."): Full escape sequences (\n, \t, \r, \\, \", \a, \b, \f, \v) are decoded via codecs.decode(). Content is preserved as-is after escape processing.
  3. Unquoted: Inline comments (whitespace + #) are stripped. Trailing whitespace is stripped. No escape processing.
context: |
  The parser determines quoting by peeking at the first character after the = sign. This single character dispatch is the core branching point of value parsing. The distinction matters most for: (a) values containing # characters, (b) values with special characters like newlines, and (c) values with trailing whitespace.
do:
  - "Use single quotes for values containing # that should not be treated as comments"
  - "Use double quotes for values needing escape sequences like \\n"
  - "Use unquoted values only for simple alphanumeric content"
dont:
  - "Put unquoted values with # in them -- everything after whitespace+# is stripped as a comment"
  - "Expect \\n to be interpreted in single-quoted values -- only \\' and \\\\ are processed"
  - "Use nested quotes -- the parser does not support 'value with \"inner\" quotes'"
applies_to_versions: ">=0.9.0"
confidence: 0.95
evidence_level: E5
sources:
  - "src/dotenv/parser.py:L128-L139 (parse_value dispatch)"
  - "src/dotenv/parser.py:L25 (_single_quoted_value regex)"
  - "src/dotenv/parser.py:L26 (_double_quoted_value regex)"
  - "src/dotenv/parser.py:L27 (_unquoted_value regex)"
  - "src/dotenv/parser.py:L122-L125 (parse_unquoted_value strips comments)"
  - "src/dotenv/parser.py:L31-L32 (escape regex patterns)"
  - "src/dotenv/parser.py:L107-L110 (decode_escapes)"
---

## Detailed Mechanics

### Parse Dispatch

```python
# src/dotenv/parser.py:L128-L139
def parse_value(reader: Reader) -> str:
    char = reader.peek(1)
    if char == "'":
        (value,) = reader.read_regex(_single_quoted_value)
        return decode_escapes(_single_quote_escapes, value)
    elif char == '"':
        (value,) = reader.read_regex(_double_quoted_value)
        return decode_escapes(_double_quote_escapes, value)
    elif char in ("", "\n", "\r"):
        return ""
    else:
        return parse_unquoted_value(reader)
```

### Escape Sequences

| Quote Type | Escape Regex | Supported Escapes |
|-----------|-------------|-------------------|
| Single `'` | `\\[\\']` | `\\` -> `\`, `\'` -> `'` |
| Double `"` | `\\[\\'\"abfnrtv]` | `\\`, `\'`, `\"`, `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v` |
| Unquoted | None | No escape processing |

### Comment Stripping (Unquoted Only)

```python
# src/dotenv/parser.py:L122-L125
def parse_unquoted_value(reader: Reader) -> str:
    (part,) = reader.read_regex(_unquoted_value)
    return re.sub(r"\s+#.*", "", part).rstrip()
```

The regex `\s+#.*` requires whitespace before `#`, so `VALUE#notacomment` is preserved but `VALUE #comment` strips `#comment`.

### Write-Side Quoting (`set_key`)

When writing values via `set_key()`, a separate `quote_mode` parameter controls output:
- `always` (default): wraps in single quotes, escapes `'` as `\'`
- `auto`: quotes only if value is not purely alphanumeric
- `never`: no quoting

**Evidence:** `src/dotenv/main.py:L209-L219`
