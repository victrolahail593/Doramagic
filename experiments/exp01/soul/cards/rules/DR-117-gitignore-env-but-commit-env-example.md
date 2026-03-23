---
card_type: decision_rule_card
card_id: DR-117
repo: python-dotenv
type: UNSAID_BEST_PRACTICE
title: "Always .gitignore .env but commit .env.example with placeholder values"
rule: |
  The .env file should always be in .gitignore to prevent accidental secret
  exposure. Provide a .env.example (or .env.template) file with all required
  keys and placeholder/default values. This serves as documentation and makes
  onboarding easy (cp .env.example .env).
context: |
  This is the most universally agreed-upon python-dotenv best practice, yet
  the python-dotenv docs only briefly mention it. The risk of committing
  .env with real secrets is catastrophic (exposed API keys, database passwords).
  GitHub has secret scanning, but it only catches known secret formats.
do:
  - "Add .env to .gitignore in every project using python-dotenv"
  - "Create .env.example with all keys and safe placeholder values"
  - "Document which variables are required vs optional in .env.example"
  - "Use git-secrets or pre-commit hooks to prevent accidental .env commits"
dont:
  - "Commit .env files to version control, even in private repos"
  - "Use real secrets as placeholder values in .env.example"
  - "Rely solely on .gitignore — add a pre-commit hook as a safety net"
applies_to_versions: ">=0.1.0"
confidence: 0.95
evidence_level: E4
sources:
  - "https://dev.to/emma_donery/python-dotenv-keep-your-secrets-safe-4ocn"
  - "https://blog.stackademic.com/mastering-data-security-in-python-a-deep-dive-into-env-files-and-python-dotenv-bf2324fc619"
  - "https://dagster.io/blog/python-environment-variables"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
