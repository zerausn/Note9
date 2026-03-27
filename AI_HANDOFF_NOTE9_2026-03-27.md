# AI Handoff: Note9 / DeX / Flow

Date: 2026-03-27
Workspace: `C:\Users\ZN-\Documents\Antigravity`
Git remote: `git@github.com:zerausn/Note9.git`
Branch at handoff time: `main`

## Purpose

This file is a restartable handoff for any future AI working on the Samsung Note9 with a bad screen.
The user wants the Note9 screen projected to this PC, to any PC, to a Samsung tablet, and if possible to a Samsung S24 Ultra.
Primary control path is ADB over USB, with ADB over Wi-Fi as a secondary option when available.

## Devices

- Note9 serial: `29396e8c1e3f7ece`
- Note9 model target in scripts: `SM_N9600`
- Tablet serial seen in local scripts: `R92Y1073GER`
- Bundled ADB path: `C:\Users\ZN-\Documents\Antigravity\scrcpy\scrcpy-win64-v3.1\adb.exe`
- Windows Samsung DeX app path: `C:\Program Files (x86)\Samsung\Samsung DeX\SamsungDeX.exe`

## Repo / Context Notes

- User said the starting point is always `Antigravity`.
- There is no clean top-level README or test harness.
- This repo mixes scripts, screenshots, XML dumps, APK pulls, logs, and local machine state.
- Many hand-captured artifacts in the repo are directly useful for resume work.

## Files Changed During This Session

These files were improved to match the real Note9 / DeX / Flow state instead of stale assumptions:

- `C:\Users\ZN-\Documents\Antigravity\auto_connect_flow.py`
- `C:\Users\ZN-\Documents\Antigravity\configurar_wifi.bat`
- `C:\Users\ZN-\Documents\Antigravity\arreglar_dex.bat`
- `C:\Users\ZN-\Documents\Antigravity\iniciar_todo.bat`

High-level change summary:

- hardcoded the known Note9 serial and model handling
- switched scripts to use bundled `adb.exe` first
- updated diagnostics to reflect real USB / DeX / Wi-Fi state
- removed reliance on stale activity names that no longer launch
- added keepalive / deviceidle handling in Python for Flow/DeX-related packages

## Important Evidence Files

Launcher / UI recovery:

- `C:\Users\ZN-\Documents\Antigravity\after_reinstall_launcher.png`
- `C:\Users\ZN-\Documents\Antigravity\after_reinstall_launcher.xml`
- `C:\Users\ZN-\Documents\Antigravity\after_disable_emergencylauncher.png`
- `C:\Users\ZN-\Documents\Antigravity\after_disable_emergencylauncher.xml`
- `C:\Users\ZN-\Documents\Antigravity\boot_now.png`
- `C:\Users\ZN-\Documents\Antigravity\boot_now.xml`

DeX / quick settings / visual attempts:

- `C:\Users\ZN-\Documents\Antigravity\dex_open_start.png`
- `C:\Users\ZN-\Documents\Antigravity\dex_open_start.xml`
- `C:\Users\ZN-\Documents\Antigravity\after_dex_tile.png`
- `C:\Users\ZN-\Documents\Antigravity\after_dex_tile.xml`
- `C:\Users\ZN-\Documents\Antigravity\mode_toggle.png`
- `C:\Users\ZN-\Documents\Antigravity\after_mode_toggle.png`
- `C:\Users\ZN-\Documents\Antigravity\qs_for_dex.png`
- `C:\Users\ZN-\Documents\Antigravity\qs_for_dex.xml`
- `C:\Users\ZN-\Documents\Antigravity\post_reboot_em_check.png`
- `C:\Users\ZN-\Documents\Antigravity\post_reboot_em_check.xml`
- `C:\Users\ZN-\Documents\Antigravity\after_dex_start_confirm.png`
- `C:\Users\ZN-\Documents\Antigravity\after_dex_start_confirm.xml`

Flow / pairing / mirroring historical artifacts:

- `C:\Users\ZN-\Documents\Antigravity\flow_pairing.xml`
- `C:\Users\ZN-\Documents\Antigravity\flow_phone.xml`
- `C:\Users\ZN-\Documents\Antigravity\flow_tablet.png`
- `C:\Users\ZN-\Documents\Antigravity\tablet_mirror_success.png`
- `C:\Users\ZN-\Documents\Antigravity\tablet_mirror_final.png`

Reverse-engineering / package state:

- `C:\Users\ZN-\Documents\Antigravity\dexonpc_package_dump.txt`
- `C:\Users\ZN-\Documents\Antigravity\DeXonPC.apk`
- `C:\Users\ZN-\Documents\Antigravity\all_packages.txt`
- `C:\Users\ZN-\Documents\Antigravity\packages_note9.txt`
- `C:\Users\ZN-\Documents\Antigravity\props.txt`

Network notes:

- `C:\Users\ZN-\Documents\Antigravity\ip_note9.txt`
- `C:\Users\ZN-\Documents\Antigravity\note9_wlan0.txt`
- `C:\Users\ZN-\Documents\Antigravity\wlan0_info.txt`
- `C:\Users\ZN-\Documents\Antigravity\arp.txt`

Power / emergency-state checks:

- `C:\Users\ZN-\Documents\Antigravity\power_after_single_press.png`
- `C:\Users\ZN-\Documents\Antigravity\power_after_single_press.xml`
- `C:\Users\ZN-\Documents\Antigravity\power_longpress.png`
- `C:\Users\ZN-\Documents\Antigravity\power_longpress.xml`
- `C:\Users\ZN-\Documents\Antigravity\after_disable_ultra_power.png`
- `C:\Users\ZN-\Documents\Antigravity\after_disable_ultra_power.xml`

## What Was Confirmed

### 1. USB ADB works

The Note9 is controllable by ADB over USB. This is the main working control path.

### 2. Wi-Fi ADB is unreliable

Wi-Fi ADB was attempted successfully at the command level (`tcpip 5555` and `adb connect`) in some cases, but timeouts suggest hotspot/client-isolation or network-path issues. Use USB as the primary path.

Historical/local IP evidence seen in files and prior commands:

- Note9 on hotspot path was seen as `10.210.41.171`
- PC was seen as `10.210.41.125`
- Another local Wi-Fi state file shows Note9 `wlan0` as `192.168.1.13`

Treat all IPs as stale until rechecked live.

### 3. Samsung DeX is installed on the phone

Confirmed packages:

- `com.sec.android.app.dexonpc`
- `com.sec.android.desktopmode.uiservice`

The phone supports DeX on PC historically. `dumpsys desktopmode` had shown past successful `DEX_ON_PC` sessions on `2026-03-17`.

### 4. Samsung Flow package was disabled and was re-enabled

`com.samsung.android.galaxycontinuity` had been disabled for the user and was re-enabled successfully earlier in the session.

### 5. Emergency Launcher was the first big UI blocker

The phone had fallen into `Emergency Launcher`, which made visual navigation misleading.

That was repaired by:

```powershell
adb shell pm clear com.sec.android.app.launcher
adb shell pm uninstall --user 0 com.sec.android.app.launcher
adb shell pm install-existing --user 0 com.sec.android.app.launcher
adb shell pm disable-user --user 0 com.sec.android.emergencylauncher
adb shell cmd shortcut clear-default-launcher --user 0
```

Result after that:

- `Emergency Launcher` no longer owned HOME
- Samsung launcher became active again
- normal launcher screenshots/xml were captured

## Current Technical Diagnosis

### Main conclusion

The current DeX failure is not primarily a Windows USB driver problem.
Windows does see the Note9 and Samsung DeX starts negotiation.
The failure happens on the phone side, inside the DeX-on-PC service path.

### Exact failure signature

Windows Samsung DeX logs showed:

- `DeviceEvent::SecureFailed`
- `USB CONNECTION FAILED`
- `ShowNoConnectionOrUnsupportedPanel ... noConn ... unsupported: 0`

This means the Windows app is showing a "no connection" state, not an "unsupported device" state.

Phone-side logcat showed:

- `Received APPATTACHED from Remote`
- `connect failed.(error:111) ReqPort 15000 (IpAddr 127.0.0.1, Port 1003)`
- after resets, another attempt used a different source port such as `1007`, but the same local failure

Interpretation:

- the PC handshake reaches the phone
- phone-side `ss_conn_daemon2` receives the event
- then the phone fails to connect to a local loopback DeX service at `127.0.0.1:15000`
- that local service is the missing/broken piece right now

### Why this matters

If the service listening on `127.0.0.1:15000` does not come up, Windows DeX will keep falling back to "no connection" even though USB is fine.

## Emergency / System State Suspicion

One suspicious state is still present:

- `getprop security.em.tstate` returns `EM`

At the same time:

- `settings get global emergency_mode` returned `0`
- `emergency_affordance_needed` was `0`

So the Note9 is not in normal user-facing emergency mode anymore, but some deeper emergency/security state may still be influencing the DeX startup path.
This is still a strong suspect because desktopmode and dexonpc listeners were observed reacting to emergency-related broadcasts.

## Later Findings In The Same Session

After the original handoff draft above, more was confirmed:

### 1. The phone was not fully in `Emergency Launcher`, but Samsung still had an emergency/ultra-power residue

The visible launcher had already been repaired, but Samsung still had these settings active:

- `settings get system emergency_mode` returned `1`
- `settings get system ultra_powersaving_mode` returned `1`

Visible symptoms matched that state:

- status area showed `Ahorro de energía máx. activado`
- notification shade behaved like a heavily restricted Samsung power state

However:

- `HOME` still resolved to `com.sec.android.app.launcher/.activities.LauncherActivity`
- `ResumedActivity` was normal Samsung launcher or Settings, not `Emergency Launcher`

This means there were two different layers:

1. `Emergency Launcher` ownership of HOME, which was already fixed
2. Samsung emergency / ultra-power settings state, which was still active later

### 2. The Samsung emergency / ultra-power settings state was manually cleared

The following settings were forced off:

```powershell
adb shell settings put system emergency_mode 0
adb shell settings put system ultra_powersaving_mode 0
adb shell settings put global emergency_mode 0
adb shell settings put global low_power 0
adb shell settings put global low_power_sticky 0
adb shell settings put global adaptive_power_saving_setting 0
```

After that:

- `system emergency_mode=0`
- `ultra_powersaving_mode=0`
- `global emergency_mode=0`
- `global low_power=0`

But even after a reboot:

- `getprop security.em.tstate` still returned `EM`

So the visible / settings-level emergency state can be cleared, but Samsung still keeps an internal emergency-related property stuck at `EM`.

### 3. Power-button behavior is normal now

Testing confirmed:

- short press of power only turned the display off into doze / AOD
- long press showed the normal Samsung power menu with `Apagar` and `Reiniciar`
- there was no visible `Modo emergencia` button on that power menu

This is evidence that the phone is no longer trapped in the obvious user-facing emergency UI.

### 4. A critical new DeX sign appeared after clearing the Samsung power state

After clearing the Samsung emergency / ultra-power settings and rebooting, a real DeX confirmation dialog appeared on the phone:

- title: `¿Comenzar a transmitir con Samsung DeX?`
- positive button: `Iniciar ahora`
- negative button: `Cancelar`

This is a major improvement because it proves the DeX UI flow can now surface on-device.

The `Iniciar ahora` button was tapped by ADB.

Immediately after that:

- the phone returned to Samsung launcher
- the DeX confirmation dialog disappeared

This means the phone accepted the prompt interaction, but the end-to-end DeX session still needs verification on the Windows side after the tap.

### 5. Current resume state after all of that

At latest check:

- Samsung launcher is still the active HOME
- Samsung emergency / ultra-power settings are off
- `security.em.tstate` still remains `EM`
- a real DeX permission/start dialog can now appear
- the user can also use `scrcpy` on the PC as a fallback visual/control path

## Things Already Tried

### Package and service reset attempts

Tried on the phone:

```powershell
adb shell pm clear com.sec.android.app.dexonpc
adb shell am force-stop com.sec.android.app.dexonpc
```

No lasting fix. Same `127.0.0.1:15000` failure returned.

### Direct service / activity starts

Tried variations such as:

```powershell
adb shell am startservice -n com.sec.android.app.dexonpc/.service.DOPService
adb shell am start-foreground-service -n com.sec.android.app.dexonpc/.service.DOPService
adb shell am startservice -a com.sec.android.app.dexonpc.action.START_DOP_SERVICE -n com.sec.android.app.dexonpc/.service.DOPService
```

Result:

- blocked by permission / non-exported restrictions

Tried direct UI activities like:

```powershell
adb shell am start -n com.sec.android.app.dexonpc/.ui.AboutActivity
```

Result:

- also blocked as non-exported from shell uid

### Broadcast / provider tricks

Tried manual USB-state rebroadcasts and content-provider access.

Result:

- blocked by Android permissions / signature-level provider permissions

### Reboot

The Note9 was rebooted.
Launcher stayed fixed after recovery, but reboot did not fix the DeX-on-PC local service problem.

### Root check

Tried:

```powershell
adb shell su -c id
```

Result:

- no accessible `su`
- no usable root path available

This matters because root would make it much easier to inspect who should be listening on `127.0.0.1:15000`.

## Reverse Engineering Notes

`DeXonPC.apk` was pulled locally and scanned enough to identify likely internal components:

- `com.sec.android.app.dexonpc.service.DOPService`
- `com.sec.android.app.dexonpc.service.DOPUsbStateReceiver`
- `com.sec.android.app.dexonpc.source.WimpService`
- `com.sec.android.app.dexonpc.kms.source.KMSService`
- `com.sec.android.app.dexonpc.action.START_DOP_SERVICE`
- `com.sec.android.app.dexonpc.action.CONNECTION_CHANGED`
- `com.sec.android.app.dexonpc.action.MAIN_SERVER_CONNECTION`
- `com.sec.android.app.dexonpc.source.action.START_WIMP_SERVICE`
- provider authority under `com.sec.android.app.dexonpc.contentprovider.multipreference.DOPProvider`

This supports the theory that the USB receiver path exists, but the service chain does not fully come up from the current phone state.

## Process State Notes

- `ss_conn_daemon2` was observed running
- no long-lived `dexonpc` user-space process was seen in `ps -A` during failed attempts

This strongly suggests the DeX app-side local server is not fully launching, even though the connection daemon sees the PC.

## Windows-Side Log Locations

Use these again on resume:

- `%APPDATA%\Samsung\Samsung DeX\SamsungDeXLog_*.log`
- `%PROGRAMDATA%\Samsung\MSSCS\connsvc2-0.log`

These were enough to determine:

- Windows recognizes the device
- failure is "no connection" / secure handshake related
- not an unsupported-device UI state

## Best Current Working Theory

The phone-side DeX-on-PC path is partially broken or suppressed.
Most likely causes, in order:

1. lingering emergency/security state interfering with startup
2. package/component state mismatch after earlier emergency-launcher issues
3. the non-exported DeX local service chain not auto-starting from the USB receiver path
4. stale internal state under `dexonpc` / desktopmode packages that simple `pm clear` did not fully repair

## Resume Plan For The Next AI

### Highest-value next steps

1. Re-check live phone state before touching anything:

```powershell
& 'C:\Users\ZN-\Documents\Antigravity\scrcpy\scrcpy-win64-v3.1\adb.exe' -s 29396e8c1e3f7ece shell getprop security.em.tstate
& 'C:\Users\ZN-\Documents\Antigravity\scrcpy\scrcpy-win64-v3.1\adb.exe' -s 29396e8c1e3f7ece shell settings get global emergency_mode
& 'C:\Users\ZN-\Documents\Antigravity\scrcpy\scrcpy-win64-v3.1\adb.exe' -s 29396e8c1e3f7ece shell dumpsys desktopmode
& 'C:\Users\ZN-\Documents\Antigravity\scrcpy\scrcpy-win64-v3.1\adb.exe' -s 29396e8c1e3f7ece shell dumpsys usb
```

2. Continue by UI automation through Settings / Samsung DeX / connected-device screens, because non-exported components cannot be launched directly from shell.

3. Verify on Windows whether the DeX session advances after the on-phone `Iniciar ahora` confirmation, using Samsung DeX logs plus fresh phone-side logcat.

4. Investigate whether the lingering `EM` state can be cleared safely without root via settings, package-state repair, Samsung emergency-mode components, or a system service reset path.

5. Keep Windows DeX open while capturing fresh logcat filtered for:

```text
dexonpc
desktopmode
ss_conn_daemon2
usb
emergency
galaxycontinuity
```

6. If DeX remains blocked, try to make Samsung Flow the primary recovery path for projection/mirroring to the tablet/PC using the already recovered launcher and the historical pairing artifacts in this repo.

### Things not to waste time on first

- re-checking whether DeX is installed: it is
- re-installing Windows USB drivers as the primary fix
- relying on stale hardcoded activity names from old scripts
- assuming old IPs are still current

## Security / Secret Handling

- The user provided an SSID name (`HILAS`) in chat.
- The hotspot password was intentionally not copied into this file.
- Re-check network credentials from the conversation or the user when needed.

## Bottom Line

The session made real progress:

- the phone is controllable over USB ADB
- Samsung launcher was repaired after the emergency-launcher issue
- a hidden Samsung emergency / ultra-power state was found and manually disabled
- Flow package was re-enabled
- DeX support was verified as present on-device
- a real on-device DeX confirmation dialog was surfaced after clearing the Samsung power-state residue
- Windows-side logs proved the problem is not simply "unsupported device"
- the real blocker was narrowed to the phone-side local DeX service path, specifically failure to connect to `127.0.0.1:15000`

That is the precise state another AI should resume from.
