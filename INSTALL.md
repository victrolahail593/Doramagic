# Installing Doramagic

## OpenClaw (recommended)

Install from ClawHub:
```bash
openclaw skills install dora
```

Or manually:
```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cp -r Doramagic/skills/doramagic ~/.openclaw/skills/dora
```

## Claude Code CLI

Copy the skill to your Claude Code skills directory:
```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
mkdir -p ~/.claude/skills
cp -r Doramagic/skills/doramagic ~/.claude/skills/dora
```

Then use it with `/dora` in Claude Code.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- At least one LLM API key:
  - `ANTHROPIC_API_KEY` (Claude)
  - `OPENAI_API_KEY` (GPT)
  - `GOOGLE_API_KEY` (Gemini)

## Configuration

Copy `models.json.example` to `models.json` and configure your available models:
```bash
cp models.json.example models.json
```

Set your API key as an environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
