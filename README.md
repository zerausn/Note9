# Note9 / Termux / OpenClaw Bridge

This repository is the Note9-side workspace for the Samsung Note9
(`SM-N9600`). It is separate from the PC-side `open-claw` repository,
which currently hosts the local Antigravity/OpenClaw manager and the
OpenAI-compatible proxy used by the phone.

## Verified State As Of 2026-03-30

- Device model: `SM-N9600`
- Android version: `10`
- Build: `QP1A.190711.020.N9600ZHU9FVI1`
- Primary ADB path: USB
- Secondary ADB path: Wi-Fi ADB after `adb tcpip 5555`
- Installed Android apps confirmed live:
  - `com.termux`
  - `com.termux.x11`
  - `studio.com.techriz.andronix`
  - `ru.meefik.linuxdeploy`
- `com.termux` is `DEBUGGABLE`, so `adb shell run-as com.termux ...` works
- Installed `proot-distro` rootfs:
  - `debian`
  - `parrot`
  - `ubuntu`
- `openclaw` is installed inside the Debian rootfs
- The PC-side Antigravity proxy is healthy at `http://127.0.0.1:8045`
  and reported version `4.1.31`

## What This Repo Now Contains

- [termux_bridge.py](./termux_bridge.py)
  Central CLI to inspect ADB state, prepare Termux, expose the PC proxy
  to the phone, and launch Debian/XFCE from Windows.
- [launch_debian_openclaw.sh](./launch_debian_openclaw.sh)
  Device-side launcher for the Debian CLI where `openclaw` is installed.
- [launch_debian_xfce.sh](./launch_debian_xfce.sh)
  Device-side launcher for the Debian XFCE session through `Termux:X11`.
- [AGENTS.md](./AGENTS.md)
  Repo-specific instructions and hard-earned context for future AI agents.
- [SESSION_NOTES_2026-03-30.md](./SESSION_NOTES_2026-03-30.md)
  Detailed notes about what was inspected, what worked, and what failed.

## Quick Start

From this repo on the Windows PC:

```powershell
python .\termux_bridge.py status
python .\termux_bridge.py prepare-termux
python .\termux_bridge.py reverse-openclaw
python .\termux_bridge.py open-debian
```

If you want to try the desktop session:

```powershell
python .\termux_bridge.py open-xfce
```

## What `prepare-termux` Does

`prepare-termux` is the reproducible setup step added in this session.
It does three things:

1. Enables `allow-external-apps = true` in
   `~/.termux/termux.properties`
2. Copies the Debian CLI and XFCE launchers into the private Termux home
3. Reloads Termux settings and tells you to relaunch the app cleanly

That matters because future Termux external app execution depends on that
property, and it leaves the launchers staged in the right place.

## What `open-debian` Does

`open-debian` opens the Debian CLI through the current ADB transport by
running the device-side launcher directly as the Termux app user:

```text
/data/data/com.termux/files/home/launch_debian_openclaw.sh
```

This was chosen because the more obvious `RunCommandService` route from
`adb shell am startservice` is blocked by `com.termux.permission.RUN_COMMAND`
for the ADB shell user on this device.

The launcher:

- restores the Termux `PATH`
- enters the Debian rootfs with `proot-distro login debian`
- exports the PC proxy variables for OpenAI-compatible tools
- opens an interactive shell in Debian over ADB

## What `open-xfce` Does

`open-xfce` runs:

```text
/data/data/com.termux/files/home/launch_debian_xfce.sh
```

That launcher:

- restores the Termux `PATH`
- starts PulseAudio if needed
- starts `termux-x11`
- starts the `Termux:X11` activity from Termux
- logs into Debian
- runs XFCE as Debian user `zerausn`

The old launcher `startxfce4_debian.sh` should be treated as stale.
It still assumes the wrong user (`droidmaster`) and fails when run without
the Termux `PATH`.

## OpenClaw And Proxy Wiring

The phone should not try to reach the PC proxy through a LAN IP.
The manager is intentionally bound to PC localhost.

Instead, use:

```powershell
python .\termux_bridge.py reverse-openclaw
```

Then inside Termux or Debian:

```bash
export OPENAI_API_KEY=sk-antigravity
export OPENAI_BASE_URL=http://127.0.0.1:8045/v1
```

Quick checks:

```bash
curl -s http://127.0.0.1:8045/health
curl -s http://127.0.0.1:8045/v1/models -H "Authorization: Bearer sk-antigravity"
```

Important model note:

- complex work last verified: `gemini-3.1-pro-high`
- faster work last verified: `gemini-3-flash`

Do not assume `gemini-3.1-flash`; the live proxy catalog on 2026-03-30
contained `gemini-3-flash`.

## Current Known-Good Findings

- USB ADB is currently the reliable control path.
- Wi-Fi ADB was re-established in this session at `10.180.101.183:5555`.
- `adb shell run-as com.termux ...` is the most reliable way to inspect
  Termux internals.
- Debian is the distro that actually contains `openclaw`.
- The Debian user for desktop sessions is `zerausn`, not `droidmaster`.
- The Debian CLI session can be opened from Termux through `proot-distro`.
- The PC-side proxy is healthy and reachable for Android through
  `adb reverse tcp:8045 tcp:8045`.

## Current Limitations

- Wi-Fi ADB is still not fully stabilized because the phone did not always
  report a usable `wlan0` address during the earlier part of this session,
  although it later recovered and reported `10.180.101.183`.
- SSH key login into Termux was not finished yet.
- XFCE launch is prepared and scripted, but it should still be treated as
  needing live end-to-end verification after each fresh boot of the phone.

## Recommended Next Steps

1. Keep using USB ADB as the recovery path.
2. Use `prepare-termux` and `open-debian` as the standard entry path.
3. Keep `reverse-openclaw` active whenever Debian/Termux should use the
   PC-side proxy.
4. Finish the SSH path inside Termux so Linux work stops depending on app
   launches.
5. Revisit Wi-Fi ADB once the phone reports a stable Wi-Fi IP again.
