# Session Notes - 2026-04-06

These notes document the second-wave cleanup after the `Antigravity` root was
reorganized as an umbrella workspace.

## Goal

Resolve the legacy Note9 shadow copies that had been left at the old root and
decide what belongs in this repo versus what should stay archived locally.

## What Was Found

The old root still contained a legacy working copy of the `Note9` project
mixed with the new umbrella workspace.

That legacy set had three kinds of content:

1. exact duplicates of files already versioned in this repo
2. shadow copies with minor or operational differences
3. root-only DeX / Flow automation, handoff notes, logs, APKs, dumps,
   screenshots, and local machine artifacts

## Decisions Made

### 1. Exact duplicates

Exact duplicates stayed archived only in the local workspace snapshot.
They were not re-imported into the repo because this repo already contains the
canonical copy.

### 2. Shadow copies with current operational value

These were merged into the canonical repo:

- `Abrir_Note9_scrcpy.bat`
- `configurar_wifi.bat`
- `bypass_dex.bat` was updated to prefer bundled `adb.exe` and explicit
  Note9 device detection
- `lanzar_scrcpy.bat` was simplified to call `Abrir_Note9_scrcpy.bat`

Rationale:

- `Abrir_Note9_scrcpy.bat` is a useful daily utility and fits the current repo
- `configurar_wifi.bat` remains relevant because Wi-Fi ADB is still part of
  the known-good operational model
- `bypass_dex.bat` is still a valid recovery helper when DeX behavior matters

### 3. Older but still useful historical automation

These were archived inside the repo under `legacy/dex-flow/`:

- `AI_HANDOFF_NOTE9_2026-03-27.md`
- `auto_connect_flow.py`
- `iniciar_todo.bat`
- `arreglar_dex.bat`

Rationale:

- they preserve real history and prior automation work
- they are not the preferred path for current OpenClaw / Termux operations
- keeping them under `legacy/` avoids polluting the active entry points

### 4. Heavy or machine-specific artifacts

These were intentionally left outside the repo in the local workspace layer:

- APKs
- package dumps
- network notes
- screenshots and XMLs unique to the legacy root
- scratch logs and other one-machine evidence

Canonical local location:

`C:\Users\ZN-\Documents\Antigravity\workspace-local\note9-ops\root-legacy`

## Current Repo Shape After This Session

Active path:

- `termux_bridge.py`
- launcher scripts for Debian / gateway / TUI / health
- `Abrir_Note9_scrcpy.bat`
- `lanzar_scrcpy.bat`
- `configurar_wifi.bat`
- `bypass_dex.bat`

Archived path:

- `legacy/dex-flow/`

## Future Work

1. Decide whether the old DeX / Flow automation should eventually be rewritten
   around the same explicit device-detection style used in the newer scripts.
2. Decide whether a small manifest of local-only artifacts should be generated
   automatically from `workspace-local/note9-ops/root-legacy`.
3. Finish the remaining umbrella cleanup in the root so the legacy `Note9`
   git history is not confused with the umbrella workspace structure.
