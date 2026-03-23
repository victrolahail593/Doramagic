---
card_type: concept_card
card_id: CC-wifipw-003
repo: sdushantha/wifi-password
title: "Cross-Platform Abstraction — Single Tool, Multiple OS Backends"
source_url: https://github.com/sdushantha/wifi-password
---

## Identity
The abstraction layer that routes credential retrieval to the correct OS-specific command while presenting a unified interface to the user. Each OS has fundamentally different storage mechanisms and access commands.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A routing/dispatch layer over OS-native commands | A hardware or network driver |
| Platform detection at runtime | A virtualization layer |
| Read-only: only extracts, never modifies | A network configuration tool |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| platform | sys.platform detection | Routes to macOS/Windows/Linux handler |
| macos_cmd | security find-generic-password | Reads from Keychain |
| windows_cmd | netsh wlan show profile key=clear | Reads from Windows credential store |
| linux_cmd | nmcli / wpa_supplicant.conf | Reads from NetworkManager or wpa config |

## Boundaries
- Starts at: sys.platform detection or explicit OS argument
- Delegates to: OS subprocess calls
- Does NOT handle: WiFi networks not previously connected, enterprise 802.1X networks (WPA-Enterprise)

## Evidence
- Source: topics list includes "linux", "macos", "windows" explicitly
- Source: Project description: "cross-platform" implied by multi-OS topic coverage
- WHY evidence level: HIGH (topic tags are explicit; multi-OS is stated design goal)
