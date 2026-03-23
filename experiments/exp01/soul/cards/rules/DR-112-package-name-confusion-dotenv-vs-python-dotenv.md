---
card_type: decision_rule_card
card_id: DR-112
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Install 'python-dotenv' not 'dotenv' — the wrong package causes silent failures"
rule: |
  The correct pip package is 'python-dotenv' (pip install python-dotenv), but
  the import is 'dotenv' (from dotenv import load_dotenv). There exists a
  separate, unrelated package called 'dotenv' on PyPI. Installing the wrong
  one gives a ModuleNotFoundError or silent misbehavior. In Docker containers,
  the wrong package may be installed if requirements.txt has a typo.
context: |
  This naming mismatch is one of the top Stack Overflow questions about
  python-dotenv. The confusion is compounded by Docker builds where
  requirements.txt errors surface only at runtime, not build time.
do:
  - "Always use 'pip install python-dotenv' in requirements.txt"
  - "Verify the installed package: pip show python-dotenv"
  - "Use 'from dotenv import load_dotenv' for imports"
dont:
  - "Put 'dotenv' in requirements.txt (it is a different, unrelated package)"
  - "Assume import errors mean python-dotenv is not installed — check which package is installed"
applies_to_versions: ">=0.1.0"
confidence: 0.95
evidence_level: E3
sources:
  - "https://discuss.python.org/t/installing-dotenv-vs-load-dotenv-why/51024"
  - "https://www.geeksforgeeks.org/python/modulenotfounderror-no-module-named-dotenv-in-python/"
  - "https://github.com/theskumar/python-dotenv/issues/283"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
