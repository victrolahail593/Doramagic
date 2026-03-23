---
card_type: decision_rule_card
card_id: DR-003
repo: python-dotenv
type: DESIGN_DECISION
title: "Interpolation Rules -- ${VAR} Expansion Behavior"
rule: |
  IF interpolate=True (default), THEN values containing ${VAR} or ${VAR:-default} are expanded.
  IF interpolate=False, THEN ${VAR} is treated as literal text.
  Only ${VAR} syntax (with braces) is recognized -- $VAR is literal.
  Only the :- (default) operator is supported -- :=, :+, :? are literal.
  Resolution is sequential: earlier .env entries are available to later ones.
  Undefined variables without defaults resolve to empty string "".
context: |
  python-dotenv implements a subset of POSIX parameter expansion. The design choice to require ${braces} and only support :- is deliberate -- it covers the most common use case (defaults) while keeping the implementation simple. The sequential processing order means .env file order matters for cross-references.
do:
  - "Use ${VAR:-default} for variables that may not be defined"
  - "Define base variables before derived variables in the .env file"
  - "Set interpolate=False when .env values contain literal ${} that should not be expanded"
dont:
  - "Use $VAR without braces and expect expansion"
  - "Use ${VAR:=value}, ${VAR:+value}, or ${VAR:?error} -- they are not supported"
  - "Expect nested expansion like ${${LEVEL}_KEY} to work"
  - "Rely on forward references -- a variable used before it is defined resolves to '' or os.environ"
applies_to_versions: ">=0.10.0"
confidence: 0.95
evidence_level: E5
sources:
  - "src/dotenv/variables.py:L5-L13 (_posix_variable regex)"
  - "src/dotenv/variables.py:L70-L86 (parse_variables tokenizer)"
  - "src/dotenv/variables.py:L63-L67 (Variable.resolve with default fallback)"
  - "src/dotenv/main.py:L289-L311 (resolve_variables sequential processing)"
  - "src/dotenv/main.py:L82-L84 (interpolate flag check in DotEnv.dict)"
---

## Detailed Mechanics

### Regex Pattern

```python
# src/dotenv/variables.py:L5-L13
_posix_variable = re.compile(
    r"""
    \$\{
        (?P<name>[^\}:]*)    # variable name: anything except } and :
        (?::-
            (?P<default>[^\}]*)  # default value: anything except }
        )?
    \}
    """,
    re.VERBOSE,
)
```

### What Gets Matched

| Input | Matched? | name | default |
|-------|----------|------|---------|
| `${HOME}` | Yes | `HOME` | `None` |
| `${DB:-localhost}` | Yes | `DB` | `localhost` |
| `${:-empty}` | Yes | `` (empty) | `empty` |
| `$HOME` | No (no braces) | -- | -- |
| `${VAR:=val}` | No (`:=` not `:-`) | -- | -- |
| `${VAR:+val}` | No (`:+` not `:-`) | -- | -- |

### Resolution Order

```python
# src/dotenv/main.py:L293-L309
for name, value in values:     # Sequential iteration
    ...
    atoms = parse_variables(value)
    env = {}
    if override:
        env.update(os.environ)
        env.update(new_values)   # Previously resolved .env entries
    else:
        env.update(new_values)
        env.update(os.environ)
    result = "".join(atom.resolve(env) for atom in atoms)
    new_values[name] = result    # Available to subsequent entries
```

### Edge Cases

1. **Empty variable name:** `${:-default}` matches with `name=""`. `env.get("", default)` returns `default` since empty string key is unlikely to exist.

2. **Default containing special chars:** `${VAR:-http://localhost:3000}` -- the `:` after `http` does NOT trigger another `:-` match because the regex is non-greedy and `:-` must appear immediately after the name. The default is `http://localhost:3000`.

3. **Variable with None value:** If an earlier entry was `KEY` (no `=`), `new_values["KEY"]` is `None`. `Variable.resolve()` handles this: `result = env.get(self.name, default)` returns `None`, then `return result if result is not None else ""` converts to empty string.
   - **Evidence:** `src/dotenv/variables.py:L63-L67`
