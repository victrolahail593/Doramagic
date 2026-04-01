---
name: dora
description: >
  Your AI Doraemon — describe a problem, get a working tool forged from 10,000+
  knowledge bricks. Use when: "help me build", "I need a tool", "dora", "doramagic"
version: 13.1.0
user-invocable: true
license: MIT-0
metadata:
  openclaw:
    emoji: "🪄"
    skillKey: dora
    category: builder
    requires:
      bins: [python3, git]
    install:
      - kind: uv
        package: "doramagic @ git+https://github.com/tangweigang-jpg/Doramagic.git@v13.1.0"
        bins: [doramagic]
---

# Doramagic — Router

IRON LAW: DO NOT START WORKING WITHOUT CLARIFYING THE REQUIREMENT FIRST.
Complete Socratic dialogue and get user confirmation before routing.

---

## Step 1: Detect Intent

| User Input | Intent | Action |
|------------|--------|--------|
| Contains `github.com/` URL | Extract | Route to `/dora-extract` |
| Contains "extract soul" / "提取灵魂" | Extract | Route to `/dora-extract` |
| `/dora-status` | Status | Run status query (Step 4) |
| Everything else | Compile | Proceed to Step 2 |

## Step 2: Socratic Dialogue (Compile intent only)

- Max 2 questions per round, multiple choice only
- Technical specifics present → skip to confirmation
- Everyday language → 2-3 rounds of guiding questions

Confirm: "I understand you need: [requirement]. Correct?" Wait for confirmation.

## Step 3: Route (Compile)

```bash
mkdir -p ~/.doramagic/sessions
cat > ~/.doramagic/sessions/latest.json << 'EOF'
{"requirement": "{confirmed requirement}", "phase": "clarified"}
EOF
```

Read `references/compile-flow.md` and follow the Match → Build flow.

## Step 4: Status Query

```bash
python3 {baseDir}/scripts/doramagic_main.py --input "/dora-status" --run-dir ~/.doramagic/runs/
```

Show `message` to user. Do NOT modify anything.

## Rules

- Respond in user's language. Never show JSON or code.
- Do NOT skip Socratic dialogue. Do NOT list options — make recommendations.
- Delegate: bricks → compile-flow, extraction → /dora-extract, status → Step 4.
