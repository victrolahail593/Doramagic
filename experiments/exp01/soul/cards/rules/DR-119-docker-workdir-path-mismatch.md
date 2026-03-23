---
card_type: decision_rule_card
card_id: DR-119
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Docker WORKDIR mismatch causes load_dotenv() to silently find no .env file"
rule: |
  In Docker containers, the working directory (set by WORKDIR in Dockerfile)
  may differ from where the .env file is copied. Since load_dotenv() defaults
  to searching from the calling file's directory (not cwd), and Docker often
  uses different directory structures than local development, the .env file
  may silently not be found. No error is raised by default.
context: |
  A common pattern: local development has .env in the project root, Docker
  COPY copies it to /app/.env, but WORKDIR is /app and the Python file calling
  load_dotenv() is in /app/src/. The search starts from /app/src/ and may not
  find /app/.env. Additionally, using Docker's --env-file flag makes python-
  dotenv's .env loading redundant, leading to double-loading or confusion.
do:
  - "Use explicit dotenv_path in Docker: load_dotenv(dotenv_path='/app/.env')"
  - "Prefer Docker's --env-file or environment: directive over embedding .env in images"
  - "Use PYTHON_DOTENV_DISABLED=1 in Docker if env vars are injected by the platform"
dont:
  - "Rely on automatic .env discovery inside Docker containers"
  - "COPY .env files into Docker images (secrets in image layers)"
  - "Use both Docker --env-file and load_dotenv() without understanding the interaction"
applies_to_versions: ">=0.1.0"
confidence: 0.85
evidence_level: E3
sources:
  - "https://github.com/theskumar/python-dotenv/issues/283"
  - "https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
