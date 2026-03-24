---
name: dora
description: >
  Doramagic — extract design wisdom from open-source projects and forge skills.
version: 9.2.0
user-invocable: true
tags: [doramagic, knowledge-extraction, skill-generation]
metadata: {"openclaw":{"emoji":"🪄","skillKey":"dora","category":"builder","requires":{"bins":["python3"],"env":["ANTHROPIC_API_KEY"]},"primaryEnv":"ANTHROPIC_API_KEY","install":[{"id":"uv","kind":"pip","package":"uv","bins":["uv"],"label":"Install uv (Python package runner)"}]}}
---

uv run {baseDir}/scripts/doramagic_main.py --input "{args}" --run-dir ~/.doramagic/runs/

---

## Protocol

Script output is JSON. Two modes:

### Normal output
Show the `message` field to the user exactly as-is.

### Clarification output
If output has `"clarification": true`, show the `question` field and wait for user's answer.
Then re-invoke with: `uv run {baseDir}/scripts/doramagic_main.py --continue {run_id} --input "{user_answer}" --run-dir ~/.doramagic/runs/`

### Progress output
If output has `"progress": true`, show the `message` field as a status update. More output will follow.

## Constraints

- Show the `message` field to the user exactly as-is.
- Do NOT add your own content, analysis, or commentary.
- Do NOT run any additional commands after the script finishes (unless clarification is needed).
- If the output has `error: true`, show the error message and stop.
