# Doramagic Compile Flow (Match → Build)

This document combines the brick matching and code generation phases.
Invoked by the main SKILL.md router when user intent is "compile/build a tool".

---

## Phase A: Brick Matching

IRON LAW: NO CODE GENERATION WITHOUT RUNNING THE BRICK MATCHING SCRIPT.

### Step 1: Read Requirement

```bash
cat ~/.doramagic/sessions/latest.json
```

Extract the `requirement` field. If missing, tell user: "Please start with /dora first."

### Step 2: Run Brick Matching

Tell user: "Matching relevant constraints from the knowledge base..."

```bash
python3 {baseDir}/scripts/doramagic_compiler.py --input "{requirement}" --user-id "default"
```

Returns JSON: `success`, `matched_bricks`, `constraint_count`, `constraint_prompt`,
`capabilities`, `limitations`, `risk_report`, `evidence_sources`.

### Step 3: Save Results

Update `~/.doramagic/sessions/latest.json` with matched results, set `phase: "matched"`.

---

## Phase B: Code Generation

IRON LAW: EVERY LINE OF GENERATED CODE MUST FOLLOW THE CONSTRAINT_PROMPT.

### Step 4: Generate Code

Generate a complete, runnable Python script that:
1. Follows every rule in `constraint_prompt`
2. Implements the user's requirement
3. Includes error handling and logging
4. Can run directly with `python3 script.py`

Save to `~/.doramagic/generated/{tool_name}.py`.

### Step 5: Verify

```bash
python3 -c "import ast; ast.parse(open('$HOME/.doramagic/generated/{tool_name}.py').read()); print('Syntax OK')"
```

If fails, fix and retry (max 3 times).

### Step 6: Run and Deliver

Run the tool, then report to user with ALL of these (mandatory):
1. **Status**: "Your tool is running!" + what it's doing
2. **Capability boundaries**: What it can and cannot do
3. **Risk warnings**: Paraphrased in simple language
4. **Knowledge sources**: "From N verified sources"

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Script not found | "Run `openclaw skills update dora`" |
| 0 bricks matched | Proceed with general knowledge, warn user |
| Script error | Show error, stop |

## Prohibited Actions

- Do NOT invent constraints from your own knowledge
- Do NOT modify the constraint_prompt from the script
- Do NOT skip running the matching script
- Do NOT show code unless user explicitly asks
- Do NOT omit capability boundaries or risk warnings
