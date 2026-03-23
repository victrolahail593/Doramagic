# Workflow Card: Variable Expansion Resolution

**Card ID:** WF-002  
**Type:** Workflow  
**Repository:** python-dotenv  

## Overview

How python-dotenv resolves variable references like `${DOMAIN}` or `${PORT:-8080}` when parsing `.env` values.

## Steps

```
┌─────────────────────────┐
│ 1. Input Value         │
│ "HOST=${DOMAIN}:${PORT}"│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 2. Tokenize            │
│ parse_variables()      │
└────────────┬────────────┘
             │ Returns: [Literal("HOST="), Variable("DOMAIN"), Literal(":"), Variable("PORT", "8080")]
             ▼
┌─────────────────────────┐
│ 3. Build Environment   │
│ Merge: .env vars + os.environ│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 4. Resolve Each Atom   │
│ atom.resolve(env)       │
│ - Literal: return as-is │
│ - Variable: lookup env  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 5. Join & Return       │
│ "HOST=example.com:8080"│
└─────────────────────────┘
```

1. **Input Value:** String containing zero or more variable references
2. **Tokenize:** Split into `Atom` objects (Literal or Variable) using regex
3. **Build Environment:** Create merged dict of .env file vars + `os.environ`
4. **Resolve:** Each `Variable.resolve()` looks up in env, uses default if missing
5. **Join:** Concatenate all resolved atoms into final string

## Failure Modes

| Scenario | Input | Result |
|----------|-------|--------|
| Undefined var, no default | `${UNDEFINED}` | `""` (empty string) |
| Undefined var with default | `${UNDEFINED:-fallback}` | `"fallback"` |
| Circular reference | `A=$B`, `B=$A` | `""` (breaks cycle) |
| Self-reference | `FOO=$FOO` | Empty or original env value |
| Empty default | `${VAR:-}` | `""` |
