import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ADB_BUNDLED = ROOT / "scrcpy" / "scrcpy-win64-v3.1" / "adb.exe"
CONFIG_FILE = ROOT / "config_dispositivos.json"
NOTE9_MODEL = "SM_N9600"
FLOW_PACKAGE = "com.samsung.android.galaxycontinuity"
DEX_PACKAGES = [
    "com.sec.android.app.dexonpc",
    "com.sec.android.app.desktoplauncher",
]
DEVICE_WHITELIST = [FLOW_PACKAGE] + DEX_PACKAGES


DEFAULT_CONFIG = {
    "phone": {
        "id": "29396e8c1e3f7ece",
        "name": "Note 9",
    },
    "tablet": {
        "id": "R92Y1073GER",
        "name": "Galaxy Tab A9+",
        "ip": "192.168.1.20",
    },
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_CONFIG


def find_adb():
    if ADB_BUNDLED.exists():
        return str(ADB_BUNDLED)
    return "adb"


ADB = find_adb()


def run_command(args, timeout=30):
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


def adb(*args, timeout=30):
    return run_command([ADB, *args], timeout=timeout)


def adb_on(device_id, *args, timeout=30):
    return adb("-s", device_id, *args, timeout=timeout)


def parse_devices(output):
    devices = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices attached"):
            continue
        parts = line.split()
        serial = parts[0]
        state = parts[1] if len(parts) > 1 else "unknown"
        metadata = {}
        for token in parts[2:]:
            if ":" in token:
                key, value = token.split(":", 1)
                metadata[key] = value
        devices.append(
            {
                "serial": serial,
                "state": state,
                "model": metadata.get("model", ""),
                "product": metadata.get("product", ""),
            }
        )
    return devices


def list_adb_devices():
    result = adb("devices", "-l")
    return parse_devices(result.stdout)


def choose_note9_device(config):
    devices = list_adb_devices()
    preferred = config.get("phone", {}).get("id")
    for device in devices:
        if device["serial"] == preferred and device["state"] == "device":
            return device
    for device in devices:
        if device["state"] == "device" and NOTE9_MODEL.lower() in device["model"].lower():
            return device
    for device in devices:
        if device["state"] == "device":
            return device
    return None


def first_ipv4(text):
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", text)
    return match.group(1) if match else None


def get_phone_ip(device_id):
    result = adb_on(device_id, "shell", "ip", "-f", "inet", "addr", "show", "wlan0")
    return first_ipv4(result.stdout)


def get_phone_route(device_id):
    result = adb_on(device_id, "shell", "ip", "route")
    return result.stdout.strip()


def get_wifi_summary(device_id):
    result = adb_on(device_id, "shell", "dumpsys", "wifi")
    text = result.stdout
    lines = []
    for line in text.splitlines():
        if "mWifiInfo" in line or "SSID:" in line:
            lines.append(line.strip())
    return "\n".join(lines[:4]) if lines else "No Wi-Fi summary found."


def package_installed(device_id, package_name):
    result = adb_on(device_id, "shell", "pm", "list", "packages", package_name)
    return package_name in result.stdout


def get_usb_state(device_id):
    result = adb_on(device_id, "shell", "dumpsys", "usb")
    keys = (
        "host_connected",
        "connected",
        "configured",
        "current_mode",
        "data_role",
        "Current DexModeObserver state",
    )
    lines = []
    for line in result.stdout.splitlines():
        if any(key in line for key in keys):
            lines.append(line.strip())
    return "\n".join(lines) if lines else "No USB state found."


def get_dex_props(device_id):
    result = adb_on(device_id, "shell", "getprop")
    keys = (
        "service.adb.tcp.port",
        "service.dexonpc.running",
        "sys.dockstate",
        "sys.usb.state",
    )
    lines = []
    for line in result.stdout.splitlines():
        if any(key in line for key in keys):
            lines.append(line.strip())
    return "\n".join(lines) if lines else "No DeX props found."


def set_keepalive_policies(device_id):
    commands = [
        ("shell", "settings", "put", "global", "adaptive_battery_management_enabled", "0"),
        ("shell", "settings", "put", "global", "app_standby_enabled", "0"),
        ("shell", "settings", "put", "global", "stay_on_while_plugged_in", "3"),
        ("shell", "dumpsys", "deviceidle", "disable"),
    ]
    for package_name in DEVICE_WHITELIST:
        commands.append(("shell", "dumpsys", "deviceidle", "whitelist", f"+{package_name}"))
    for command in commands:
        adb_on(device_id, *command)


def restart_adb_tcpip(device_id, port=5555):
    return adb_on(device_id, "tcpip", str(port))


def connect_wifi_adb(ip_address, port=5555):
    return adb("connect", f"{ip_address}:{port}", timeout=35)


def get_host_ipv4_addresses():
    try:
        host = socket.gethostname()
        _, _, ip_list = socket.gethostbyname_ex(host)
        return sorted({ip for ip in ip_list if "." in ip and not ip.startswith("127.")})
    except OSError:
        return []


def maybe_connect_tablet(config):
    tablet = config.get("tablet", {})
    tablet_ip = tablet.get("ip")
    if not tablet_ip:
        return "Tablet IP not configured."
    result = connect_wifi_adb(tablet_ip)
    if "connected to" in result.stdout.lower() or "already connected" in result.stdout.lower():
        return f"Tablet ADB over Wi-Fi OK at {tablet_ip}:5555"
    return f"Tablet ADB over Wi-Fi failed at {tablet_ip}:5555 -> {result.stdout.strip() or result.stderr.strip()}"


def print_section(title, body):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(body)
    print()


def main():
    config = load_config()
    device = choose_note9_device(config)
    if not device:
        print("No ADB device found. Connect the Note9 by USB first.")
        sys.exit(1)

    phone_id = device["serial"]
    set_keepalive_policies(phone_id)

    wifi_summary = get_wifi_summary(phone_id)
    phone_ip = get_phone_ip(phone_id)
    route_summary = get_phone_route(phone_id)
    usb_state = get_usb_state(phone_id)
    dex_props = get_dex_props(phone_id)
    host_ips = ", ".join(get_host_ipv4_addresses()) or "Unknown"

    wifi_result = "No Wi-Fi IP found on wlan0."
    tcpip_result = restart_adb_tcpip(phone_id).stdout.strip()

    if phone_ip:
        time.sleep(2)
        connect_result = connect_wifi_adb(phone_ip)
        wifi_result = connect_result.stdout.strip() or connect_result.stderr.strip()

    package_lines = []
    for package_name in [FLOW_PACKAGE] + DEX_PACKAGES:
        package_lines.append(f"{package_name}: {'installed' if package_installed(phone_id, package_name) else 'missing'}")

    note_lines = [
        "Legacy activity names in the old scripts are stale.",
        "ADB and Samsung USB drivers can be healthy even when DeX is not running.",
        "If Wi-Fi ADB still times out on a mobile hotspot, client isolation is the most likely cause.",
    ]

    print_section(
        "Phone",
        f"Selected device: {phone_id}\nModel hint: {device.get('model') or 'unknown'}\nHost IPv4s: {host_ips}",
    )
    print_section("Wi-Fi", f"{wifi_summary}\n\nRoute: {route_summary}\nCurrent phone IP: {phone_ip or 'unknown'}")
    print_section("ADB over Wi-Fi", f"tcpip result: {tcpip_result}\nconnect result: {wifi_result}")
    print_section("USB / DeX", f"{usb_state}\n\n{dex_props}\n\n" + "\n".join(package_lines))
    print_section("Tablet", maybe_connect_tablet(config))
    print_section("Notes", "\n".join(note_lines))


if __name__ == "__main__":
    main()
