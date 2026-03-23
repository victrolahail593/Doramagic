---
card_type: decision_rule_card
card_id: DR-120
repo: python-dotenv
type: UNSAID_BEST_PRACTICE
title: "load_dotenv() mutates global state — prefer dotenv_values() for explicit configuration"
rule: |
  load_dotenv() modifies the global os.environ dictionary, which is shared
  across all threads and modules. This side effect makes code harder to test,
  debug, and reason about. For more explicit and testable configuration,
  dotenv_values() returns a plain dict without touching os.environ. You can
  then selectively assign values or pass the dict to your configuration layer.
context: |
  The "load_dotenv is an anti-pattern" argument centers on this global state
  mutation. In complex applications with multiple configuration sources (env
  vars, .env files, config files, CLI args), having load_dotenv() silently
  modify os.environ makes it unclear which source provided a given value.
  Using dotenv_values() gives you full control over the configuration pipeline.
do:
  - "Use dotenv_values() when you need fine-grained control over configuration"
  - "Combine dotenv_values() with Pydantic Settings or a custom config class"
  - "Audit where load_dotenv() is called in your codebase — ideally only once"
dont:
  - "Call load_dotenv() from multiple modules hoping they compose cleanly"
  - "Use load_dotenv() in library code (leave .env loading to the application)"
  - "Assume os.environ accurately reflects your .env file after load_dotenv()"
applies_to_versions: ">=0.1.0"
confidence: 0.85
evidence_level: E3
sources:
  - "https://dev.to/proteusiq/trending-anti-pattern-loading-environments-j55"
  - "https://safjan.com/use-decouple-with-pydantic-or-python-dataclass-to-manage-configuration-in-py/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
