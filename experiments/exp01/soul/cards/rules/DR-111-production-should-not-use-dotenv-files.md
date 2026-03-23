---
card_type: decision_rule_card
card_id: DR-111
repo: python-dotenv
type: UNSAID_BEST_PRACTICE
title: "Do not use .env files in production — use platform-native secrets management"
rule: |
  python-dotenv is designed for development convenience. In production, environment
  variables should be injected by the platform (Docker, Kubernetes, Heroku, systemd,
  AWS ECS) or managed by a secrets manager (AWS Secrets Manager, HashiCorp Vault,
  Azure Key Vault). Shipping .env files to production creates security risks and
  deployment fragility.
context: |
  .env files in production are problematic because: (1) they must be deployed
  alongside code, creating a secret-distribution problem; (2) they are plain-text
  files on disk, readable by any process with file access; (3) they are not
  rotatable without redeployment; (4) they may be accidentally committed to
  version control. The PYTHON_DOTENV_DISABLED=1 flag (added mid-2025) allows
  disabling load_dotenv() in production without code changes.
do:
  - "Use PYTHON_DOTENV_DISABLED=1 in production to prevent .env loading"
  - "Inject env vars via the deployment platform (Docker --env-file, K8s ConfigMap/Secret)"
  - "Use a secrets manager for sensitive values"
  - "Guard load_dotenv() calls: if not os.getenv('PRODUCTION'): load_dotenv()"
dont:
  - "Ship .env files in Docker images or production deployments"
  - "Rely on .env files as the sole configuration mechanism in production"
  - "Store production secrets in .env files committed to version control"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E3
sources:
  - "https://dev.to/proteusiq/trending-anti-pattern-loading-environments-j55"
  - "https://github.com/theskumar/python-dotenv/issues/510"
  - "https://dagster.io/blog/python-environment-variables"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
