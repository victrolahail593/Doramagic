---
card_type: concept_card
card_id: CC-wifipw-001
repo: rauchg/wifi-password
title: "OS Keychain / Credential Store — Primary Storage Backend"
source_url: https://github.com/rauchg/wifi-password
---

## Identity
The operating system's native credential store (macOS Keychain, Windows Credential Manager, Linux wpa_supplicant conf) is the single source of truth for stored WiFi passwords. The tool retrieves from it, never stores independently.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A read-only retrieval adapter over the OS credential store | A new password storage system |
| OS-native: reads from Keychain/wpa_supplicant/netsh | A cross-platform encrypted vault |
| Zero-copy security model (doesn't persist anything new) | A WiFi password generator or setter |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| storage_backend | OS-dependent | Where credentials actually live |
| retrieval_method | shell command / API call | How to extract the stored value |
| scope | current user session | Access limited to authenticated user |

## Boundaries
- Starts at: User is already connected to or was previously connected to the WiFi network
- Delegates to: OS keychain APIs (security command on macOS, netsh on Windows, nmcli/wpa on Linux)
- Does NOT handle: Network discovery, password setting, multi-user access

## Evidence
- Source: macOS uses `security find-generic-password -D "AirPort network password"` system command
- Source: README documents OS-specific commands
- WHY evidence level: MEDIUM (behavior inferred from shell script, no explicit design doc)
