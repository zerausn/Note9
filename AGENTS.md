# AGENTS.md - Note9 Repo Context

This repository is the Note9-side half of a larger setup that also includes
the PC-side `open-claw` repo and a local Antigravity/OpenClaw proxy running
on the Windows host.

If you are another AI agent entering this repo, read this file first and
then read [SESSION_NOTES_2026-03-31.md](./SESSION_NOTES_2026-03-31.md).

## Scope And Boundaries

- Repo path: `C:\Users\ZN-\Documents\Antigravity\Openclaw note 9`
- GitHub remote: `git@github.com:zerausn/Note9.git`
- This repo is for the phone, ADB, Termux, Linux-on-Android, and control
  tooling around the Note9.
- The Windows-side Antigravity/OpenClaw manager lives elsewhere, mainly in
  the `open-claw` repo.

## Current Device Truths

- Device serial: `29396e8c1e3f7ece`
- Model: `SM-N9600`
- Android: `10`
- Build: `QP1A.190711.020.N9600ZHU9FVI1`
- USB ADB is currently the reliable path.
- Wi-Fi ADB also recovered during this session at `10.180.101.183:5555`.
- Once USB and Wi-Fi ADB are both connected, raw `adb` commands need `-s`.

## Current Proxy Truths

- Health URL: `http://127.0.0.1:8045/health`
- Base URL: `http://127.0.0.1:8045/v1`
- API key: `sk-antigravity`
- Last verified manager version: `4.1.31`
- Last verified complex model: `gemini-3.1-pro-high`
- Last verified fast model: `gemini-3-flash`

Do not assume `gemini-3.1-flash`. The live model list verified on
2026-03-30 exposed `gemini-3-flash`.

## Termux / Linux Truths

- `com.termux` is `DEBUGGABLE`
- `adb shell run-as com.termux ...` works and is much more reliable than
  blind typing into the UI
- Installed rootfs under `proot-distro`:
  - `debian`
  - `parrot`
  - `ubuntu`
- The distro that actually contains `openclaw` is `debian`
- Debian contains user `zerausn`
- The old GUI launcher scripts still reference `droidmaster` and should be
  treated as stale unless rewritten
- `openclaw` by itself prints CLI help
- the usable terminal UI command is `openclaw tui`
- `openclaw tui` needs `openclaw gateway` already running
- the reliable automation path is now launcher scripts + `run-as com.termux`,
  not UI typing

## Important Paths

- Termux home:
  `/data/data/com.termux/files/home`
- Termux properties:
  `/data/data/com.termux/files/home/.termux/termux.properties`
- Debian rootfs:
  `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian`
- `openclaw` binary:
  `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/usr/bin/openclaw`
- `openclaw` config directory:
  `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/root/.openclaw`

## Current Repo Entry Points

- [termux_bridge.py](./termux_bridge.py)
  Main Windows-side helper
- [launch_debian_openclaw.sh](./launch_debian_openclaw.sh)
  CLI launcher copied into Termux home
- [launch_debian_xfce.sh](./launch_debian_xfce.sh)
  XFCE launcher copied into Termux home
- [launch_openclaw_gateway.sh](./launch_openclaw_gateway.sh)
  OpenClaw gateway launcher for Debian
- [launch_openclaw_tui.sh](./launch_openclaw_tui.sh)
  OpenClaw TUI launcher for Debian
- [check_openclaw_health.sh](./check_openclaw_health.sh)
  OpenClaw health checker for Debian

## Use These Commands First

```powershell
python .\termux_bridge.py status
python .\termux_bridge.py prepare-termux
python .\termux_bridge.py openclaw-up
```

For piecewise OpenClaw control:

```powershell
python .\termux_bridge.py reverse-openclaw
python .\termux_bridge.py openclaw-gateway
python .\termux_bridge.py openclaw-health
python .\termux_bridge.py openclaw-tui
```

## Known Pitfalls

- Do not trust old scripts like `startxfce4_debian.sh` as-is.
  They fail because:
  - they run without the Termux `PATH`
  - they still use `droidmaster`
- Do not assume `adb shell am startservice ... RunCommandService` is a valid
  launch path from the ADB shell user.
  It hit a permission denial for `com.termux.permission.RUN_COMMAND`.
- Do not assume SSH is fully configured.
  `sshd` was started before, but key-based login was not finished.
- Do not assume Wi-Fi ADB is alive.
  Re-check `wlan0` from live ADB before using `adb connect`.
- Prefer `adb reverse tcp:8045 tcp:8045` over LAN routing for the proxy.
- Do not assume `openclaw` alone opens the app you want.
  It prints help; use `openclaw tui`.
- Do not assume `termux-run` or raw `adb shell input text` is reliable enough
  for complex commands on this phone.
- Do not assume one-shot shell autostart files in Termux will execute.
  `.bashrc`, `.bash_profile`, `.profile`, and `.bash_login` were tested and
  did not auto-fire in the way hoped for.

## If You Need To Inspect The Phone Again

Prefer these patterns:

```powershell
adb devices -l
adb shell run-as com.termux ls -la /data/data/com.termux/files/home
adb shell run-as com.termux ls -la /data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs
adb shell run-as com.termux cat /data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/etc/passwd
adb shell run-as com.termux /data/data/com.termux/files/usr/bin/proot-distro login debian -- /bin/bash -lc "whoami; pwd"
```

## Current Strategy

1. Recover or keep USB ADB first.
2. Keep Termux automation reproducible through `termux_bridge.py`.
3. Use `adb reverse` so Debian/Termux can reach the PC proxy on localhost.
4. Use Debian as the Linux environment for `openclaw`.
5. Use `openclaw-up` as the preferred automation path for daily use.
6. Finish SSH later, but do not block the current TUI/gateway path on it.

## Related But Separate Root Snapshot

Root was evaluated but not attempted in this session.
The last-known device state from the earlier check was:

- bootloader locked
- Knox not yet tripped
- OEM unlock support present but not currently allowed

That root context is informational only here. It is not part of the current
Termux/OpenClaw workflow.

## Documentation Priority

If you change the real operational path, update all three:

1. `README.md`
2. `AGENTS.md`
3. the newest `SESSION_NOTES_YYYY-MM-DD.md`

This repo is being used as living operational memory, not just code storage.
