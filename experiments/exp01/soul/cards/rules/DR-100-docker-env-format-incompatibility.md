---
card_type: decision_rule_card
card_id: DR-100
repo: python-dotenv
type: UNSAID_COMPATIBILITY
title: "Docker Compose and python-dotenv parse .env files differently"
rule: |
  python-dotenv follows Bash-like quoting semantics (interpreting escape sequences
  in double quotes, performing variable interpolation with ${VAR}), while Docker
  Compose uses a simpler, more literal parsing. The same .env file can produce
  different values in each tool, especially around quotes, backslashes, and
  variable expansion.
context: |
  Many projects use a single .env file for both Docker Compose (docker-compose.yml
  env_file directive) and python-dotenv (load_dotenv in app code). Because the
  parsers differ, values containing quotes, backslashes, or dollar signs can
  silently diverge between local dev (python-dotenv) and container runtime (Docker).
  This is a well-known issue (GitHub #92) with no built-in compatibility mode.
do:
  - "Test .env values in both Docker Compose and python-dotenv if sharing one file"
  - "Use simple alphanumeric values without quotes when possible for cross-tool compatibility"
  - "Consider separate .env files for Docker and app-level loading"
  - "Prefer Docker's --env-file flag or environment: block for container-specific vars"
dont:
  - "Assume a .env file that works with python-dotenv will produce identical values in Docker Compose"
  - "Use escape sequences or variable interpolation if the file must be Docker-compatible"
  - "Use single quotes in values intended for Docker Compose (Docker does not strip them)"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E3
sources:
  - "https://github.com/theskumar/python-dotenv/issues/92"
  - "https://github.com/docker/compose/issues/7903"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
