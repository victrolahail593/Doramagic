---
card_type: concept_card
card_id: CC-wifipw-002
repo: sdushantha/wifi-password
title: "QR Code Export — Zero-Friction Device Sharing"
source_url: https://github.com/sdushantha/wifi-password
---

## Identity
QR code generation as an output format for WiFi credentials, enabling device-to-device sharing without manual typing. The credential stays in the OS store; QR is a transient display artifact.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A convenience display format for credential sharing | Persistent QR storage |
| Ephemeral: QR generated at request time, not cached | A network manager or captive portal |
| Optional feature layered on top of retrieval | Secure channel (QR visible to anyone nearby) |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| qr_library | qrcode (Python) | Generates printable WiFi QR in WPA standard format |
| wifi_qr_format | `WIFI:T:WPA;S:{ssid};P:{password};;` | IEEE 802.11 compatible QR format |
| terminal_output | boolean | Show QR in terminal vs save as image |

## Boundaries
- Starts at: Password successfully retrieved from OS store
- Delegates to: qrcode library for rendering
- Does NOT handle: QR scanning, password validation, network joining

## Evidence
- Source: sdushantha/wifi-password README: "generate a QR code of your WiFi to allow phones to easily connect"
- Source: topics include "qrcode"
- WHY evidence level: HIGH (explicit feature description in README)
