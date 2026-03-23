---
card_type: decision_card
card_id: DC-wifipw-002
repo: sdushantha/wifi-password
title: "CLI vs. GUI: Why Terminal-First for Credential Retrieval"
severity: MEDIUM
source_url: https://github.com/sdushantha/wifi-password
---

## 决策
IF building a WiFi password retrieval tool for developers/power users,
THEN implement as a CLI tool rather than a GUI application.

## 理由
The target user (developer who forgets their own WiFi password and needs to retrieve it quickly, or wants to share with a guest) benefits more from:
1. Scriptability: `wifi-password | pbcopy` or pipe to other tools
2. Fast invocation: single command, no window to open
3. SSH compatibility: can retrieve remotely when managing servers

The QR code feature in sdushantha/wifi-password acknowledges the "share with others" use case and solves it without requiring a GUI.

## 替代方案
- **GUI application**: Higher development cost, harder to script, OS-specific UI toolkits
- **Web interface**: Security concern (exposes credentials over HTTP, even localhost)
- **System tray app**: Complex lifecycle, harder to test, requires persistent daemon

## Do
- Support stdout output for piping: `wifi-password wifi-name | clip`
- Support QR code in terminal (`--qrcode` flag) for sharing without additional software
- Exit with meaningful error codes (0 = found, 1 = not found, 2 = permission denied)

## Don't
- Launch a GUI for a task that is fundamentally a read operation
- Require a daemon or background process for one-shot retrieval
- Open a browser window to display the password

## Evidence
- sdushantha/wifi-password: Python CLI with argparse interface
- rauchg/wifi-password: pure bash one-liner
- WHY evidence: MEDIUM (both projects chose CLI; cross-project consensus)
- Cross-project validation: YES (two independent projects made same design choice)
