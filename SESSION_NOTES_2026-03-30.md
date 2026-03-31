# Session Notes - 2026-03-30

These notes preserve the exact context of the Note9, Termux, Debian, XFCE,
and OpenClaw work completed in this session.

## Goal

Resume work on the `Note9` repo, recover the context of the Note9 and
`open-claw`, and start using Termux plus the Linux environment where
`openclaw` was installed through ADB and later ADB over Wi-Fi.

## High-Level Outcome

- The correct Linux environment was identified as the Debian rootfs inside
  Termux `proot-distro`.
- `openclaw` was confirmed inside Debian.
- Termux was prepared for controlled external launching.
- Repo-side launchers were created for Debian CLI and Debian XFCE.
- A reproducible Windows helper CLI was expanded in `termux_bridge.py`.
- The repo was documented so a future AI or operator does not need to
  rediscover the same facts.

## Live Facts Verified In This Session

### Phone

- Serial: `29396e8c1e3f7ece`
- Model: `SM-N9600`
- Android: `10`
- Build: `QP1A.190711.020.N9600ZHU9FVI1`

### PC Proxy

- `http://127.0.0.1:8045/health` returned `{"status":"ok","version":"4.1.31"}`
- The model catalog was reachable and contained at least:
  - `gemini-3.1-pro-high`
  - `gemini-3-flash`
  - `claude-sonnet-4-6`
  - `claude-opus-4-6`
- Important correction:
  the live fast Gemini model is `gemini-3-flash`, not `gemini-3.1-flash`

## Android App Inventory Confirmed Live

- `com.termux`
- `com.termux.x11`
- `studio.com.techriz.andronix`
- `ru.meefik.linuxdeploy`

## Termux Findings That Changed The Strategy

### 1. `run-as com.termux` works

This was the biggest unlock.

`adb shell dumpsys package com.termux` showed:

- `DEBUGGABLE`

That means `adb shell run-as com.termux ...` can inspect the private Termux
data directory directly. This is far more reliable than typing blind into
the app UI.

### 2. Installed rootfs were identified

Inside:

`/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs`

the live rootfs found were:

- `debian`
- `parrot`
- `ubuntu`

### 3. Debian is the distro that contains `openclaw`

Confirmed paths:

- `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/usr/bin/openclaw`
- `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/usr/lib/node_modules/openclaw`
- `/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/root/.openclaw`

### 4. Debian user mismatch was discovered

`/etc/passwd` inside Debian contains:

- `root`
- `zerausn`

It does not contain `droidmaster`.

That explains why the existing Debian GUI launchers were wrong.

## Existing Device-Side Scripts Found

Inside Termux home:

- `startcinnamon_debian.sh`
- `startgnome_debian.sh`
- `startkde_debian.sh`
- `startlxde_debian.sh`
- `startxfce4_debian.sh`

The old `startxfce4_debian.sh` was inspected and found to:

- assume Debian user `droidmaster`
- call `pulseaudio`, `termux-x11`, and `proot-distro` by bare name

When launched outside a proper Termux login context, it fails because the
Termux `PATH` is missing.

The captured failure log showed:

- `pulseaudio: command not found`
- `termux-x11: command not found`
- `proot-distro: command not found`

## Direct Debian Access Findings

The Debian rootfs could be entered directly with:

```powershell
adb shell run-as com.termux /data/data/com.termux/files/usr/bin/proot-distro login debian -- /bin/bash -lc "whoami; pwd"
```

Observed output:

- `root`
- `/`

That proved the Debian CLI environment itself was accessible.

## OpenClaw Relationship

`openclaw` on the phone is inside the Debian rootfs and should be treated as
the Linux-side runtime.

The PC-side Antigravity/OpenClaw manager remains on Windows and should be
reached from the phone through:

```text
adb reverse tcp:8045 tcp:8045
```

Then inside Termux or Debian:

```bash
export OPENAI_API_KEY=sk-antigravity
export OPENAI_BASE_URL=http://127.0.0.1:8045/v1
```

Later in the session, `python .\termux_bridge.py reverse-openclaw` was run
successfully again and `status` reported:

- `UsbFfs tcp:8045 tcp:8045`

## SSH Status

Earlier in the broader workflow, `sshd` inside Termux had been started and a
local forward to `127.0.0.1:8022` was validated. However, key-based login
was not completed successfully, so SSH should still be considered unfinished.

## Wi-Fi ADB Status

USB ADB is currently the reliable path.

Earlier in the session, Wi-Fi ADB was not reliable because the phone was not
always reporting a usable `wlan0` IP.

Later in the same session, `status` reported:

- `wlan0 IP: 10.180.101.183`

and the command:

```powershell
python .\termux_bridge.py --ip 10.180.101.183 wifi
```

succeeded with:

- `restarting in TCP mode port: 5555`
- `connected to 10.180.101.183:5555`

That means Wi-Fi ADB became available again, but once both USB and Wi-Fi
transports are live, raw `adb` commands need explicit `-s`.

## Files Added In This Session

### Repo-side

- `README.md`
- `AGENTS.md`
- `SESSION_NOTES_2026-03-30.md`
- `termux_bridge.py`
- `launch_debian_openclaw.sh`
- `launch_debian_xfce.sh`

### Device-side deployed into Termux home

- `/data/data/com.termux/files/home/launch_debian_openclaw.sh`
- `/data/data/com.termux/files/home/launch_debian_xfce.sh`

## New Repo-Side Launchers

### `launch_debian_openclaw.sh`

Purpose:

- restore the Termux execution environment
- enter Debian with `proot-distro`
- export the proxy variables
- open an interactive Debian shell in the environment where `openclaw` lives

### `launch_debian_xfce.sh`

Purpose:

- restore the Termux `PATH`
- start `pulseaudio`
- start `termux-x11`
- open the `Termux:X11` activity
- log into Debian
- run XFCE as `zerausn`

## `termux_bridge.py` Purpose

This script became the reproducible Windows-side control plane for:

- ADB status checks
- promoting USB ADB to Wi-Fi ADB
- app launching
- `adb reverse` for the PC proxy
- `adb forward` for Termux SSH
- preparing Termux for external launchers
- opening Debian CLI
- opening Debian XFCE

## RunCommandService Dead End

An attempted automation path used:

```text
adb shell am startservice ... com.termux/.app.RunCommandService
```

This should be treated as a dead end for the ADB shell user on this phone.

The relevant log line was:

- `Permission Denial: Accessing service com.termux/.app.RunCommandService ... requires com.termux.permission.RUN_COMMAND`

Because of that, the repo switched to a more honest and reliable approach:

- use `prepare-termux` to stage files and settings
- use direct `adb shell run-as com.termux ...` to run the launcher scripts

## Recommended Operational Path After This Session

1. Keep USB ADB alive.
2. Run `python .\termux_bridge.py prepare-termux`.
3. Run `python .\termux_bridge.py reverse-openclaw`.
4. Run `python .\termux_bridge.py open-debian`.
5. Use Debian as the Linux-side `openclaw` environment.
6. Treat `open-xfce` as the next GUI step, but verify it live each time.

`open-debian` now means opening Debian over the ADB transport, not injecting
commands into the visible Termux UI.

## Things A Future AI Should Not Redo Blindly

- Do not keep using blind `adb shell input text` for complex Termux work if
  `run-as com.termux` can be used instead.
- Do not trust the legacy Debian GUI launchers without checking the user and
  `PATH`.
- Do not assume `gemini-3.1-flash`; verify the live model list first.
- Do not route the phone to the PC proxy through a LAN IP if `adb reverse`
  is available.

## Related Root Snapshot

Rooting the phone was researched but not performed in this session.
The earlier device snapshot was:

- bootloader locked
- Knox not tripped
- OEM unlock support present
- OEM unlock not currently allowed

This is useful context, but it is not part of the current Termux/OpenClaw
workflow and should not block work on Debian/ADB.
