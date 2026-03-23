---
card_type: workflow_card
card_id: WF-002
repo: python-dotenv
title: "Parsing Flow -- Stream to Bindings"
---

## Overview

How `parser.py` transforms a raw text stream into structured `Binding` tuples, handling the full `.env` grammar including quoting, escapes, comments, and error recovery.

## Steps

### Step 1: Stream Ingestion
`Reader.__init__()` reads the entire stream into a single string and initializes position tracking at `(chars=0, line=1)`.
- **Evidence:** `src/dotenv/parser.py:L72-L75`

### Step 2: Binding Loop
`parse_stream()` enters a `while reader.has_next()` loop, calling `parse_binding()` for each logical line.
- **Evidence:** `src/dotenv/parser.py:L179-L182`

### Step 3: Whitespace & Export Consumption
Within `parse_binding()`, leading multiline whitespace is consumed, then the optional `export` keyword prefix.
- **Evidence:** `src/dotenv/parser.py:L145-L153`

### Step 4: Key Parsing
`parse_key()` peeks at the first character:
- `#` -> comment line, return `key=None`
- `'` -> single-quoted key via `_single_quoted_key` regex
- Otherwise -> unquoted key via `_unquoted_key` regex
- **Evidence:** `src/dotenv/parser.py:L112-L120`

### Step 5: Value Parsing
If `=` is present, `parse_value()` dispatches on the first character after `=`:
- `'` -> single-quoted value, decode `\'` escapes
- `"` -> double-quoted value, decode `\"`, `\n`, `\t`, etc.
- empty/newline -> empty string
- Otherwise -> unquoted value, strip inline comments (`\s+#.*`)
- **Evidence:** `src/dotenv/parser.py:L128-L139`

### Step 6: Tail Consumption & Output
Consume optional trailing comment and end-of-line. Return `Binding(key, value, original, error=False)`.
- **Evidence:** `src/dotenv/parser.py:L161-L168`

### Step 7: Error Recovery
If any regex match fails (raises `Error`), consume rest-of-line with `_rest_of_line` and return `Binding(key=None, value=None, original, error=True)`.
- **Evidence:** `src/dotenv/parser.py:L169-L175`

## Flowchart

```mermaid
flowchart TD
    A["parse_stream(stream)"] --> B["Reader: read entire stream into string"]
    B --> C{"reader.has_next()?"}
    C -- No --> END["Done: iterator exhausted"]
    C -- Yes --> D["parse_binding()"]
    D --> E["set_mark(), consume whitespace"]
    E --> F{"has_next()?"}
    F -- No --> G["Return empty Binding"]
    F -- Yes --> H["Consume optional 'export' prefix"]
    H --> I["parse_key()"]
    I --> J{"First char?"}
    J -- "#" --> K["key = None (comment line)"]
    J -- "'" --> L["Single-quoted key"]
    J -- other --> M["Unquoted key"]
    K --> N["Consume comment + EOL"]
    L --> O["Consume whitespace after key"]
    M --> O
    O --> P{"peek == '='?"}
    P -- No --> Q["value = None"]
    P -- Yes --> R["Consume '=' + whitespace"]
    R --> S["parse_value()"]
    S --> T{"First char after '='?"}
    T -- "'" --> U["Single-quoted: decode \\' escapes"]
    T -- '"' --> V["Double-quoted: decode \\n \\t etc."]
    T -- "empty/newline" --> W["value = empty string"]
    T -- other --> X["Unquoted: strip inline #comments"]
    U --> N
    V --> N
    W --> N
    X --> N
    Q --> N
    N --> Y["Return Binding(key, value, original, error=False)"]
    Y --> C

    D -- "Error raised" --> Z["Consume rest_of_line"]
    Z --> AA["Return Binding(None, None, original, error=True)"]
    AA --> C
```

## Failure Modes

1. **Unclosed quote:** If a single or double quote is opened but never closed, the `_single_quoted_value` or `_double_quoted_value` regex fails to match, raising `Error`. The entire line is consumed as an error binding. The parser continues with the next line.
   - **Evidence:** `src/dotenv/parser.py:L131-L135` (regex patterns require closing quotes)

2. **Key with special characters:** If a key contains `=`, `#`, or whitespace (without being quoted), `_unquoted_key` regex `([^=\#\s]+)` will capture only the portion before the special character. This may lead to unexpected parsing where part of the key is treated as whitespace or value.
   - **Evidence:** `src/dotenv/parser.py:L23` (`_unquoted_key` pattern)

3. **Binary/non-UTF8 content:** The `Reader` calls `stream.read()` which may raise if the stream's encoding doesn't match the actual content. This error propagates uncaught.
   - **Evidence:** `src/dotenv/parser.py:L73`

4. **Multiline values in double quotes with embedded newlines:** The `_double_quoted_value` regex uses `[^"]*` which does NOT have `re.DOTALL`, but the `re.UNICODE` flag is set. Actual newlines within double-quoted values are supported because `[^"]` matches `\n` by default in Python regex. However, this is a subtle behavior dependency.
   - **Evidence:** `src/dotenv/parser.py:L26`
