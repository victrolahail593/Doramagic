---
card_type: trap_card
card_id: TC-wifipw-001
repo: sdushantha/wifi-password
title: "sudo Required on Linux — Permission Denied Silently Fails"
severity: HIGH
source_url: https://github.com/sdushantha/wifi-password
sources:
  - "Common issue pattern: Linux users reporting permission errors"
  - "wpa_supplicant.conf is root-owned: /etc/wpa_supplicant/wpa_supplicant.conf"
  - "nmcli requires network manager group or root for key display"
---

## 陷阱描述
On Linux, WiFi passwords are stored in root-owned files (`/etc/wpa_supplicant/wpa_supplicant.conf`) or accessible only via privileged nmcli commands. Running the tool as a normal user returns an empty result or a generic "not found" error with no indication that permissions are the actual problem.

## 真实场景
You install `wifi-password` on Ubuntu, run it from your regular terminal session, and get `Password not found for NetworkName`. You spend 20 minutes trying different network names, checking spelling, wondering if the password was never saved — before someone on the internet mentions you need `sudo nmcli -s con show NetworkName | grep -i psk`.

## 根因
Linux WiFi credential storage is designed for system services (NetworkManager, wpa_supplicant) that run as root. The security model deliberately prevents unprivileged reads. The tool typically doesn't distinguish "network not known" from "insufficient permissions", returning the same output for both.

## 如何避免
- Always run with `sudo` on Linux: `sudo wifi-password [network-name]`
- Or add your user to the `netdev` group (may allow nmcli key display without sudo)
- Check permissions first: `ls -la /etc/wpa_supplicant/`
- If deploying as a service, run under a user with explicit network manager permissions

## 影响范围
- 谁会遇到：Linux users, especially Ubuntu/Debian with NetworkManager
- 什么时候：First run on any Linux system without elevated privileges
- 多严重：Silent failure — no error message, just wrong output, wastes significant debug time
