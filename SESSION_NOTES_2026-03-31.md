# Session Notes - 2026-03-31

These notes continue the Note9 / Termux / Debian / OpenClaw work from
2026-03-30 and document the first successful OpenClaw TUI + gateway flow
that was automated without needing the user to type the whole sequence by hand.

## Goal

Open OpenClaw on the Note9 so it could be used immediately, then preserve:

- what worked
- what failed
- how the final automation was done

## What Was Already True Before This Session

- The Note9 ADB stack was already alive.
- Debian inside `proot-distro` had already been identified as the distro
  containing `openclaw`.
- The PC-side proxy at `http://127.0.0.1:8045` was healthy.
- `adb reverse tcp:8045 tcp:8045` had already been used successfully before.
- `run-as com.termux` had already been established as the reliable control path.

## Live State Verified Again On 2026-03-31

- PC proxy health:
  - `{"status":"ok","version":"4.1.31"}`
- ADB transports:
  - USB serial `29396e8c1e3f7ece`
  - Wi-Fi ADB `10.180.101.183:5555`
- `status` showed the expected Android apps:
  - `com.termux`
  - `com.termux.x11`
  - `studio.com.techriz.andronix`
  - `ru.meefik.linuxdeploy`

## The Important OpenClaw Discovery

The user tried:

```bash
openclaw
```

inside Debian and saw the CLI usage output.

That was the key correction:

- `openclaw` alone prints the general CLI help
- the actual terminal interface is:

```bash
openclaw tui
```

When the user ran `openclaw tui`, the UI did open, but it reported:

- `gateway disconnected: closed | idle`

That proved two things:

1. the TUI itself was fine
2. the missing piece was the OpenClaw gateway

## What Worked

### 1. Direct launcher execution with `run-as com.termux`

This remained the most reliable approach.

The launcher that opens Debian was already known-good:

- `/data/data/com.termux/files/home/launch_debian_openclaw.sh`

Using:

```powershell
adb -s 29396e8c1e3f7ece shell run-as com.termux /data/data/com.termux/files/home/launch_debian_openclaw.sh
```

still opened Debian correctly.

### 2. `openclaw --help` and `openclaw tui`

Inside Debian:

- `openclaw --help` printed the expected help
- `openclaw tui` opened the interface

### 3. A separate gateway process

The fix for the disconnected TUI was to run:

```bash
openclaw gateway
```

from the same Debian rootfs, but in a separate terminal window so it could
stay alive while the TUI connected to it.

### 4. `openclaw health`

Once the gateway was started, `openclaw health` returned healthy output
including:

- `Telegram: ok (@Oandroidbot)`
- `Agents: main (default)`
- `Heartbeat interval: 30m (main)`

That became the verification step before opening the TUI again.

### 5. Process verification

After the successful run, the Note9 process list showed the relevant pieces:

- `openclaw-gateway`
- `openclaw-tui`
- parent `openclaw` processes
- `proot`

This confirmed the real runtime on the phone, not just a hopeful UI state.

## What Did Not Work Reliably

### 1. `termux-run` / raw UI typing

Attempting to inject commands into the visible Termux UI through:

- `termux_bridge.py termux-run ...`
- `adb shell input text ...`

was still not reliable enough for complex commands on this Samsung/Termux
combination.

Even after enabling:

- `enforce-char-based-input = true`

the typed commands were not trustworthy enough to use as the main path.

### 2. One-shot shell autostart hooks

A one-shot automatic launch was attempted by writing startup hooks into:

- `.bashrc`
- `.bash_profile`
- `.profile`
- `.bash_login`

along with a marker file that should have made Termux auto-exec OpenClaw
when the app was opened.

This did not fire automatically on this Termux build.

The marker file remained present, which showed the hooks were not being
consumed in the expected way.

Those temporary hooks were later removed.

### 3. Inline `adb ... -lc "..."` quoting for some OpenClaw commands

Some attempts to run more complex OpenClaw commands inline through one-shot
ADB strings produced misleading output such as:

- `/system/bin/sh: openclaw: inaccessible or not found`
- `/system/bin/sh: cd: /root: No such file or directory`

That did not match the already verified reality that `openclaw` existed and
worked in Debian.

The lesson was:

- avoid complex nested quoting for important runtime actions
- prefer device-side scripts copied into Termux home

## How The Working Automation Was Built

### Step 1. Device-side launcher scripts were created

Three dedicated scripts were prepared on the phone:

- `launch_openclaw_gateway.sh`
- `launch_openclaw_tui.sh`
- `check_openclaw_health.sh`

Their job is simple:

- restore the Termux environment
- enter Debian through `proot-distro`
- export the proxy variables
- run exactly one OpenClaw command

### Step 2. Those scripts were brought into the repo

To avoid losing this knowledge, the same scripts were added to the repo so
future deployment is reproducible.

### Step 3. `termux_bridge.py` was expanded

New subcommands were added so the flow is no longer trapped in ad hoc shell
history:

- `openclaw-gateway`
- `openclaw-health`
- `openclaw-tui`
- `openclaw-up`

### Step 4. `openclaw-up` became the automated happy path

`openclaw-up` now does the following automatically:

1. sync launcher scripts into Termux home
2. ensure `adb reverse tcp:8045 tcp:8045` is active
3. start the gateway in a new Windows console window
4. wait and poll `openclaw health`
5. if healthy, open the TUI in another new Windows console window

This is the first automation path that matches what really worked in practice.

## Why Separate Windows Were Necessary

`openclaw gateway` is a long-running service.
`openclaw tui` is an interactive client that wants the gateway already alive.

So the practical arrangement is:

- one terminal/window keeps the gateway running
- another terminal/window runs the TUI

That is why the repo now intentionally spawns detached console windows for
these two commands.

## Final State Reached In This Session

- The OpenClaw TUI was opened on the Note9.
- The earlier `gateway disconnected` problem was traced to the gateway not
  being started, not to a broken TUI.
- The gateway was started successfully.
- Health checks passed.
- The successful flow was translated into repo-side launchers and
  `termux_bridge.py` commands.

## Recommended Daily-Use Command After This Session

From Windows in this repo:

```powershell
python .\termux_bridge.py openclaw-up
```

If you want to control the pieces separately:

```powershell
python .\termux_bridge.py openclaw-gateway
python .\termux_bridge.py openclaw-health
python .\termux_bridge.py openclaw-tui
```

## Operator Notes

- The `proot warning: can't sanitize binding "/proc/self/fd/1"` warning is
  noisy but not the actual blocker here.
- `bash: no job control in this shell` is expected in this ADB/proot context.
- The real blocking condition for the TUI was simply a missing gateway.

## Relationship To The Previous Session Note

`SESSION_NOTES_2026-03-30.md` explains how Debian, ADB, and `run-as` became
the foundation.

This file explains how that foundation was extended into a working OpenClaw
runtime that starts with minimal manual intervention.
