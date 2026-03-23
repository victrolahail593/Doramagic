---
card_type: trap_card
card_id: TC-wifipw-002
repo: rauchg/wifi-password
title: "macOS Keychain Access Dialog — Automation Breaks on macOS Sonoma+"
severity: HIGH
source_url: https://github.com/rauchg/wifi-password
sources:
  - "macOS security hardening: Keychain access now requires explicit user approval per-app"
  - "GitHub issue pattern: 'password prompt appearing' after macOS upgrade"
  - "Apple developer docs: security framework changes in macOS 13+"
---

## 陷阱描述
On macOS Ventura and later, the `security find-generic-password` command for AirPort passwords triggers a user-approval dialog each time it's called, unless the calling application has been explicitly approved in Keychain Access settings. In automated/scripted contexts (cron jobs, CI scripts, SSH sessions), this dialog may appear on the remote display or silently timeout.

## 真实场景
You set up a shell script on your Mac that grabs the WiFi password and QR-codes it for guests. It works fine in your terminal. You then try to call it via SSH from another machine or from a cron job. The `security` command hangs indefinitely waiting for a Keychain approval dialog that appears on the physical Mac screen — not in your SSH session. Your script times out or hangs forever.

## 根因
Apple's security hardening starting in macOS 13 requires explicit per-application Keychain authorization. The dialog appears on the currently-active display session, not on the caller's session. This is a security feature, not a bug. The tool (rauchg/wifi-password) is a shell script with no mechanism to pre-authorize or handle this.

## 如何避免
- For interactive use: run directly in a terminal session (not via SSH) to see and approve the dialog
- For automation: pre-authorize the calling app in Keychain Access > Access Control
- For server contexts: consider storing the password in a separate secrets manager rather than relying on Keychain scripting
- Test your automation on the target macOS version before deploying

## 影响范围
- 谁会遇到：macOS Ventura+ users running via SSH, cron, or automation frameworks
- 什么时候：First run after macOS upgrade, or first run via any non-interactive session
- 多严重：Complete failure in automated contexts; script hangs with no error message
