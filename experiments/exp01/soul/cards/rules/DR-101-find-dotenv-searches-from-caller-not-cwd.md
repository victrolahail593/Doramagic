---
card_type: decision_rule_card
card_id: DR-101
repo: python-dotenv
type: UNSAID_GOTCHA
title: "find_dotenv() searches from the calling file's directory, not the current working directory"
rule: |
  By default, find_dotenv() starts searching from the directory containing the
  Python file that calls it (using sys._getframe()), not from os.getcwd(). This
  means if load_dotenv() is called from a library or utility module in a
  different directory, it will search upward from that module's location, not
  from where you launched the process.
context: |
  This is one of the most frequently reported issues (GitHub #265, #108). When
  a base class or shared module in /lib/utils.py calls load_dotenv(), it searches
  from /lib/ upward, potentially finding a different .env file or none at all.
  The workaround is to pass usecwd=True to find_dotenv(), or to provide an
  explicit dotenv_path.
do:
  - "Use find_dotenv(usecwd=True) if you want to search from the working directory"
  - "Use an explicit dotenv_path=... argument for deterministic behavior"
  - "Call load_dotenv() from your project's entry point, not from shared libraries"
dont:
  - "Assume find_dotenv() starts from the current working directory"
  - "Call load_dotenv() without arguments from deeply nested library modules"
  - "Rely on automatic file discovery in Docker containers where cwd may differ from the app root"
applies_to_versions: ">=0.9.0"
confidence: 0.95
evidence_level: E5
sources:
  - "https://github.com/theskumar/python-dotenv/issues/265"
  - "https://github.com/theskumar/python-dotenv/issues/108"
  - "Source code: main.py find_dotenv() uses sys._getframe() to determine caller location"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
