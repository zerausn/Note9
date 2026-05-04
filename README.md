# Note9 / Termux / OpenClaw Bridge

This repository is the Note9-side workspace for the Samsung Note9
(`SM-N9600`). It is separate from the PC-side `open-claw` repository,
which currently hosts the local Antigravity/OpenClaw manager and the
OpenAI-compatible proxy used by the phone.

## Verified State As Of 2026-03-31

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
- `openclaw tui` opens on the Note9 when the gateway is already running
- `openclaw gateway` and `openclaw health` can be started from the Note9
  Debian rootfs through `run-as com.termux`

## What This Repo Now Contains

- [termux_bridge.py](./termux_bridge.py)
  Central CLI to inspect ADB state, prepare Termux, expose the PC proxy
  to the phone, and launch Debian/XFCE from Windows.
- [Abrir_Note9_scrcpy.bat](./Abrir_Note9_scrcpy.bat)
  Windows helper to open the Note9 over `scrcpy` using the bundled ADB path.
- [configurar_wifi.bat](./configurar_wifi.bat)
  Windows helper to switch the phone to `adb tcpip 5555` and print current
  Wi-Fi state before attempting `adb connect`.
- [launch_debian_openclaw.sh](./launch_debian_openclaw.sh)
  Device-side launcher for the Debian CLI where `openclaw` is installed.
- [launch_debian_xfce.sh](./launch_debian_xfce.sh)
  Device-side launcher for the Debian XFCE session through `Termux:X11`.
- [AGENTS.md](./AGENTS.md)
  Repo-specific instructions and hard-earned context for future AI agents.
- [SESSION_NOTES_2026-03-30.md](./SESSION_NOTES_2026-03-30.md)
  Detailed notes about what was inspected, what worked, and what failed.
- [SESSION_NOTES_2026-03-31.md](./SESSION_NOTES_2026-03-31.md)
  Follow-up notes for the TUI/gateway automation that was completed later.
- [launch_openclaw_gateway.sh](./launch_openclaw_gateway.sh)
  Device-side launcher for `openclaw gateway` inside Debian.
- [launch_openclaw_tui.sh](./launch_openclaw_tui.sh)
  Device-side launcher for `openclaw tui` inside Debian.
- [check_openclaw_health.sh](./check_openclaw_health.sh)
  Device-side launcher for `openclaw health` inside Debian.
- [legacy/dex-flow/](./legacy/dex-flow)
  Archived DeX / Samsung Flow automation and handoff material rescued from
  the old root snapshot.

## Quick Start

From this repo on the Windows PC:

```powershell
python .\termux_bridge.py status
python .\termux_bridge.py prepare-termux
python .\termux_bridge.py reverse-openclaw
python .\termux_bridge.py open-debian
```

If you want the full OpenClaw flow with no manual terminal typing on the PC:

```powershell
python .\termux_bridge.py openclaw-up
```

If you only want screen mirroring or Wi-Fi ADB helpers:

```powershell
.\Abrir_Note9_scrcpy.bat
.\configurar_wifi.bat
```

If you want to manage the pieces separately:

```powershell
python .\termux_bridge.py openclaw-gateway
python .\termux_bridge.py openclaw-health
python .\termux_bridge.py openclaw-tui
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
2. Copies the Debian, XFCE, and OpenClaw launchers into the private Termux home
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

## What `openclaw-up` Does

`openclaw-up` is the automated flow that matched what actually worked on
2026-03-31.

It does this in order:

1. syncs the OpenClaw launcher scripts into Termux home
2. ensures `adb reverse tcp:8045 tcp:8045` is active
3. starts `openclaw gateway` in a new Windows console window
4. waits and checks `openclaw health` from the Note9 Debian rootfs
5. opens `openclaw tui` in a second Windows console window

This is the current best automated path because it does not depend on
blindly typing into the visible Termux app.

## OpenClaw Runtime Reality

Inside the Debian rootfs:

- `openclaw` by itself prints the CLI help
- `openclaw tui` opens the terminal UI
- `openclaw tui` shows `gateway disconnected` until `openclaw gateway`
  is running
- `openclaw health` is the quickest way to confirm the gateway is ready

The successful end-to-end sequence on 2026-03-31 was:

```powershell
python .\termux_bridge.py openclaw-up
```

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
- `openclaw gateway` can be started from Debian and stays up on the Note9.
- `openclaw health` reported healthy after the gateway was started.
- `openclaw tui` connected correctly once the gateway was running.

## Current Limitations

- Wi-Fi ADB is still not fully stabilized because the phone did not always
  report a usable `wlan0` address during the earlier part of this session,
  although it later recovered and reported `10.180.101.183`.
- SSH key login into Termux was not finished yet.
- XFCE launch is prepared and scripted, but it should still be treated as
  needing live end-to-end verification after each fresh boot of the phone.
- `termux-run` and direct `adb shell input text` are still not reliable
  enough for complex commands on this Samsung build.
- one-shot shell autostart through `.bashrc`, `.bash_profile`, `.profile`,
  and `.bash_login` was attempted and did not fire automatically in Termux.

## Legacy Root Snapshot

The old `Antigravity` root used to double as a working copy of `Note9`, which
left extra DeX / Flow scripts and machine-local artifacts mixed with the new
umbrella workspace.

That second-wave cleanup was split like this:

- current utilities promoted into this repo
- older DeX / Flow automation moved into [`legacy/dex-flow/`](./legacy/dex-flow)
- bulky or machine-specific artifacts kept in the local workspace archive

Local archive path:

`C:\Users\ZN-\Documents\Antigravity\workspace-local\note9-ops\root-legacy`

## Recommended Next Steps

1. Use `openclaw-up` when you want OpenClaw ready with the least friction.
2. Keep `reverse-openclaw` active whenever Debian/Termux should use the
   PC-side proxy.
3. Keep using `run-as com.termux` launchers instead of UI typing for any
   important workflow.
4. Finish the SSH path inside Termux so Linux work stops depending on app
   launches.
5. Revisit XFCE only after the CLI/TUI flow is stable enough for daily use.
