---
card_type: decision_card
card_id: DC-wifipw-001
repo: rauchg/wifi-password
title: "Read from OS Keychain vs. Maintain Own Password Database"
severity: HIGH
source_url: https://github.com/rauchg/wifi-password
---

## 决策
IF you need to retrieve a WiFi password,
THEN use the OS native credential store (Keychain/netsh/nmcli) rather than building a separate database.

## 理由
The OS already stores WiFi passwords when you connect to a network. Duplicating this into a separate encrypted database creates:
1. Sync complexity: two stores can diverge
2. Security surface: another place for credentials to be stolen
3. User friction: requires import/export steps

The "read-only from OS store" pattern is the correct design because the OS is the single source of truth. You didn't put the password there manually — the OS captured it when you joined the network.

## 替代方案
- **Separate encrypted vault (KeePass-style)**: Rejected because requires manual population; OS already has the data
- **Cloud sync**: Rejected because it creates security exposure for no gain over local retrieval
- **Database with import**: Rejected because it creates stale-data problem

## Do
- Shell out to `security`, `netsh`, or `nmcli` to read OS-native credential stores
- Treat the OS store as authoritative and read-only
- Handle "network not found" gracefully (network might have been forgotten)

## Don't
- Create a separate password.json / SQLite database that mirrors the OS store
- Store passwords in plain text in any file
- Cache retrieved passwords beyond the immediate session

## Evidence
- rauchg/wifi-password: entire implementation is a shell one-liner around `security` command
- WHY evidence: MEDIUM (inferred from minimal implementation — no storage = no alternative considered necessary)
- Rationale Support Ratio: 0.4 (2 evidence points / 5 assertions)
