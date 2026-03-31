import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ADB_BUNDLED = ROOT / "scrcpy" / "scrcpy-win64-v3.1" / "adb.exe"

NOTE9_SERIAL = "29396e8c1e3f7ece"
LAST_KNOWN_WIFI_IP = "192.168.1.13"
ADB_TCP_PORT = 5555
SSHD_PORT = 8022
PROXY_PORT = 8045
PROXY_HOST = "127.0.0.1"
PROXY_API_KEY = "sk-antigravity"
PROXY_BASE_URL = f"http://{PROXY_HOST}:{PROXY_PORT}/v1"
PROXY_HEALTH_URL = f"http://{PROXY_HOST}:{PROXY_PORT}/health"
DEFAULT_COMPLEX_MODEL = "gemini-3.1-pro-high"
DEFAULT_FAST_MODEL = "gemini-3-flash"
TERMUX_TAP_X = 720
TERMUX_TAP_Y = 860
TERMUX_PACKAGE = "com.termux"
TERMUX_HOME = "/data/data/com.termux/files/home"
TERMUX_PROPERTIES = f"{TERMUX_HOME}/.termux/termux.properties"
TERMUX_DOWNLOAD_DIR = "/sdcard/Download"
TERMUX_EXTERNAL_APPS_PATTERN = re.compile(
    r"(?m)^allow-external-apps\s*=\s*true\s*$"
)

LAUNCHER_MAP = {
    "open-debian": "launch_debian_openclaw.sh",
    "open-xfce": "launch_debian_xfce.sh",
}

PACKAGE_MAP = {
    "termux": "com.termux",
    "termux-x11": "com.termux.x11",
    "andronix": "studio.com.techriz.andronix",
    "linuxdeploy": "ru.meefik.linuxdeploy",
}


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
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def adb(*args, timeout=30):
    return run_command([ADB, *args], timeout=timeout)


def adb_on(device_id, *args, timeout=30):
    return adb("-s", device_id, *args, timeout=timeout)


def termux_run_as(device_id, *args, timeout=30):
    return adb_on(device_id, "shell", "run-as", TERMUX_PACKAGE, *args, timeout=timeout)


def parse_devices(output):
    devices = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("List of devices attached"):
            continue
        parts = line.split()
        serial = parts[0]
        state = parts[1] if len(parts) > 1 else "unknown"
        devices.append({"serial": serial, "state": state, "raw": line})
    return devices


def list_devices():
    return parse_devices(adb("devices", "-l").stdout)


def find_live_device(ip_hint=None, port=ADB_TCP_PORT):
    devices = list_devices()

    for device in devices:
        if device["serial"] == NOTE9_SERIAL and device["state"] == "device":
            return device["serial"]

    if ip_hint:
        wifi_serial = f"{ip_hint}:{port}"
        for device in devices:
            if device["serial"] == wifi_serial and device["state"] == "device":
                return device["serial"]

    for device in devices:
        if device["state"] == "device":
            return device["serial"]

    return None


def first_ipv4(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            value = line.split()[1]
            if "/" in value:
                return value.split("/", 1)[0]
        if "inet addr:" in line:
            return line.split("inet addr:", 1)[1].split()[0]
    return None


def get_wlan0_ip(device_id):
    candidates = [
        adb_on(device_id, "shell", "ip", "-f", "inet", "addr", "show", "wlan0"),
        adb_on(device_id, "shell", "ifconfig", "wlan0"),
        adb_on(device_id, "shell", "getprop", "dhcp.wlan0.ipaddress"),
    ]

    for result in candidates:
        value = first_ipv4(result.stdout) or result.stdout.strip()
        if value:
            return value

    return None


def package_installed(device_id, package_name):
    result = adb_on(device_id, "shell", "pm", "list", "packages", package_name)
    return package_name in result.stdout


def ensure_live_device(ip_hint):
    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)
    if not selected:
        print("No live ADB device found. Recover USB or Wi-Fi ADB first.")
        return None
    return selected


def write_temp_utf8(contents):
    temp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        suffix=".tmp",
        delete=False,
    )
    with temp:
        temp.write(contents)
    return Path(temp.name)


def push_to_termux_home(device_id, local_path, device_name):
    stage_path = f"{TERMUX_DOWNLOAD_DIR}/{device_name}"
    push_result = adb_on(device_id, "push", str(local_path), stage_path, timeout=60)
    if push_result.returncode != 0:
        print((push_result.stdout or push_result.stderr).strip())
        return False

    copy_result = termux_run_as(
        device_id,
        "cp",
        stage_path,
        f"{TERMUX_HOME}/{device_name}",
        timeout=30,
    )
    if copy_result.returncode != 0:
        print((copy_result.stdout or copy_result.stderr).strip())
        return False

    chmod_result = termux_run_as(
        device_id,
        "chmod",
        "700",
        f"{TERMUX_HOME}/{device_name}",
        timeout=30,
    )
    if chmod_result.returncode != 0:
        print((chmod_result.stdout or chmod_result.stderr).strip())
        return False

    adb_on(device_id, "shell", "rm", "-f", stage_path, timeout=20)
    return True


def prepare_termux_properties(device_id):
    current = termux_run_as(device_id, "cat", TERMUX_PROPERTIES, timeout=30)
    if current.returncode != 0:
        print((current.stdout or current.stderr).strip())
        return False

    contents = current.stdout
    if not TERMUX_EXTERNAL_APPS_PATTERN.search(contents):
        contents = contents.rstrip("\r\n") + "\nallow-external-apps = true\n"

    local_temp = write_temp_utf8(contents)
    stage_path = f"{TERMUX_DOWNLOAD_DIR}/termux.properties.codex"

    try:
        backup = termux_run_as(
            device_id,
            "cp",
            TERMUX_PROPERTIES,
            f"{TERMUX_PROPERTIES}.codex.bak",
            timeout=20,
        )
        if backup.returncode != 0:
            print((backup.stdout or backup.stderr).strip())
            return False

        push_result = adb_on(device_id, "push", str(local_temp), stage_path, timeout=60)
        if push_result.returncode != 0:
            print((push_result.stdout or push_result.stderr).strip())
            return False

        replace = termux_run_as(device_id, "cp", stage_path, TERMUX_PROPERTIES, timeout=20)
        if replace.returncode != 0:
            print((replace.stdout or replace.stderr).strip())
            return False

        reload_result = termux_run_as(
            device_id,
            "/data/data/com.termux/files/usr/bin/termux-reload-settings",
            timeout=20,
        )
        if reload_result.returncode != 0:
            print((reload_result.stdout or reload_result.stderr).strip())
            return False
    finally:
        try:
            local_temp.unlink()
        except FileNotFoundError:
            pass
        adb_on(device_id, "shell", "rm", "-f", stage_path, timeout=20)

    return True


def install_termux_launchers(device_id):
    success = True
    for script_name in LAUNCHER_MAP.values():
        local_path = ROOT / script_name
        if not local_path.exists():
            print(f"Missing launcher in repo: {local_path}")
            success = False
            continue
        pushed = push_to_termux_home(device_id, local_path, script_name)
        success = success and pushed
    return success


def prepare_termux(ip_hint):
    selected = ensure_live_device(ip_hint)
    if not selected:
        return 1

    if not package_installed(selected, TERMUX_PACKAGE):
        print("Termux is not installed on the current device.")
        return 1

    print_header("Prepare Termux")

    if not prepare_termux_properties(selected):
        print("Failed while updating termux.properties.")
        return 1

    if not install_termux_launchers(selected):
        print("Failed while installing launchers into Termux home.")
        return 1

    adb_on(selected, "shell", "am", "force-stop", TERMUX_PACKAGE, timeout=20)

    print("Prepared Termux successfully.")
    print(f"- allow-external-apps enabled in {TERMUX_PROPERTIES}")
    for script_name in LAUNCHER_MAP.values():
        print(f"- installed {TERMUX_HOME}/{script_name}")
    print("- Termux was force-stopped so it restarts cleanly on next launch.")
    return 0


def spawn_interactive(args):
    return subprocess.run(args).returncode


def start_termux_launcher(device_id, script_name):
    script_path = f"{TERMUX_HOME}/{script_name}"
    return spawn_interactive(
        [
            ADB,
            "-s",
            device_id,
            "shell",
            "run-as",
            TERMUX_PACKAGE,
            script_path,
        ]
    )


def open_termux_target(command_name, ip_hint):
    script_name = LAUNCHER_MAP[command_name]
    selected = ensure_live_device(ip_hint)
    if not selected:
        return 1

    print_header(f"Launch {command_name}")
    if command_name == "open-debian":
        print("This opens Debian over the current ADB transport.")
        print("Exit the Debian shell normally when you are done.")
        return start_termux_launcher(selected, script_name)

    if command_name == "open-xfce":
        print("This starts the Debian XFCE launcher through Termux.")
        print("Verify the Termux:X11 window live after launch.")
        return start_termux_launcher(selected, script_name)

    return 0


def get_proxy_health():
    try:
        with urllib.request.urlopen(PROXY_HEALTH_URL, timeout=5) as response:
            raw = response.read().decode("utf-8", errors="replace")
        payload = json.loads(raw)
        return {"ok": True, "payload": payload}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def list_reverse_mappings(device_id):
    result = adb_on(device_id, "reverse", "--list")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def print_termux_proxy_exports():
    print("Inside Termux, use this proxy wiring:")
    print(f"export OPENAI_API_KEY={PROXY_API_KEY}")
    print(f"export OPENAI_BASE_URL={PROXY_BASE_URL}")
    print()
    print("Quick checks from Termux:")
    print(f"curl -s http://127.0.0.1:{PROXY_PORT}/health")
    print(
        "curl -s "
        f"http://127.0.0.1:{PROXY_PORT}/v1/models "
        f"-H \"Authorization: Bearer {PROXY_API_KEY}\""
    )
    print()
    print("Suggested models from Termux/OpenAI-compatible clients:")
    print(f"- complex work: {DEFAULT_COMPLEX_MODEL}")
    print(f"- faster work:  {DEFAULT_FAST_MODEL}")


def encode_input_text(command):
    return command.replace(" ", "%s")


def print_header(title):
    print("=" * 60)
    print(title)
    print("=" * 60)


def show_status(ip_hint):
    adb("start-server")
    devices = list_devices()

    print_header("PC Proxy")
    proxy = get_proxy_health()
    if proxy["ok"]:
        payload = proxy["payload"]
        print(f"Health: ok")
        print(f"Version: {payload.get('version', 'unknown')}")
        print(f"Base URL for Termux: {PROXY_BASE_URL}")
    else:
        print("Health: unavailable")
        print(f"Error: {proxy['error']}")
        print("Start the local manager before exposing it to Termux.")
    print()

    print_header("ADB Status")
    if not devices:
        print("No live ADB devices found.")
        print(f"Expected USB serial: {NOTE9_SERIAL}")
        print(f"Last known Wi-Fi ADB IP: {ip_hint}:{ADB_TCP_PORT}")
        print()
        print("Next recovery path:")
        print("1. Connect the Note9 by USB and authorize USB debugging.")
        print("2. Run: python .\\termux_bridge.py wifi")
        print("3. Then run: python .\\termux_bridge.py launch termux")
        return 1

    for device in devices:
        print(device["raw"])

    selected = find_live_device(ip_hint=ip_hint)
    print()
    print(f"Selected device: {selected or 'none'}")

    if not selected:
        return 1

    print_header("Phone Network")
    phone_ip = get_wlan0_ip(selected)
    print(f"wlan0 IP: {phone_ip or 'unknown'}")

    print_header("Linux / Termux Stack")
    for label, package_name in PACKAGE_MAP.items():
        state = "installed" if package_installed(selected, package_name) else "missing"
        print(f"{label:12} {state:9} {package_name}")

    print_header("ADB Reverse")
    reverse_mappings = list_reverse_mappings(selected)
    if reverse_mappings:
        for mapping in reverse_mappings:
            print(mapping)
    else:
        print("No reverse mappings are active yet.")

    return 0


def connect_wifi(ip_hint):
    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)

    if selected == NOTE9_SERIAL:
        print_header("Promote USB ADB To Wi-Fi")
        tcpip_result = adb_on(selected, "tcpip", str(ADB_TCP_PORT))
        print((tcpip_result.stdout or tcpip_result.stderr).strip())
        time.sleep(2)
        phone_ip = get_wlan0_ip(selected) or ip_hint
        if not phone_ip:
            print("Could not determine phone Wi-Fi IP from live ADB.")
            return 1
        connect_result = adb("connect", f"{phone_ip}:{ADB_TCP_PORT}", timeout=35)
        print((connect_result.stdout or connect_result.stderr).strip())
        return 0

    print_header("Direct Wi-Fi ADB Attempt")
    connect_result = adb("connect", f"{ip_hint}:{ADB_TCP_PORT}", timeout=35)
    print((connect_result.stdout or connect_result.stderr).strip())
    return 0 if connect_result.returncode == 0 else 1


def launch_app(app_name, ip_hint):
    if app_name not in PACKAGE_MAP:
        print(f"Unknown app target: {app_name}")
        return 1

    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)
    if not selected:
        print("No live ADB device found. Recover USB or Wi-Fi ADB first.")
        return 1

    package_name = PACKAGE_MAP[app_name]
    if not package_installed(selected, package_name):
        print(f"Package is not installed on the current device: {package_name}")
        return 1

    print_header(f"Launching {app_name}")
    result = adb_on(
        selected,
        "shell",
        "monkey",
        "-p",
        package_name,
        "-c",
        "android.intent.category.LAUNCHER",
        "1",
    )
    print((result.stdout or result.stderr).strip())
    return 0 if result.returncode == 0 else 1


def run_termux_command(command_parts, ip_hint):
    command = " ".join(command_parts).strip()
    if not command:
        print("No Termux command was provided.")
        return 1

    launch_result = launch_app("termux", ip_hint)
    if launch_result != 0:
        return launch_result

    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)
    if not selected:
        print("No live ADB device found. Recover USB or Wi-Fi ADB first.")
        return 1

    print_header("Run Inside Termux")
    print(f"Command: {command}")
    adb_on(selected, "shell", "input", "tap", str(TERMUX_TAP_X), str(TERMUX_TAP_Y))
    time.sleep(0.6)
    typed = adb_on(selected, "shell", "input", "text", encode_input_text(command))
    if typed.returncode != 0:
        print((typed.stdout or typed.stderr).strip())
        return 1
    time.sleep(0.4)
    adb_on(selected, "shell", "input", "keyevent", "66")
    print("Sent to the active Termux session.")
    return 0


def forward_ssh(ip_hint):
    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)
    if not selected:
        print("No live ADB device found. Recover USB or Wi-Fi ADB first.")
        return 1

    print_header("Forward Termux SSH")
    result = adb_on(selected, "forward", f"tcp:{SSHD_PORT}", f"tcp:{SSHD_PORT}")
    output = (result.stdout or result.stderr).strip()
    if output:
        print(output)
    print(f"Local forward ready: 127.0.0.1:{SSHD_PORT} -> device:{SSHD_PORT}")
    print("Next command after sshd is live inside Termux:")
    print(f"ssh -p {SSHD_PORT} <termux-user>@127.0.0.1")
    return 0 if result.returncode == 0 else 1


def reverse_openclaw(ip_hint):
    proxy = get_proxy_health()
    if not proxy["ok"]:
        print("The local Antigravity/OpenClaw proxy is not healthy yet.")
        print(f"Expected health URL: {PROXY_HEALTH_URL}")
        print(f"Error: {proxy['error']}")
        return 1

    adb("start-server")
    selected = find_live_device(ip_hint=ip_hint)
    if not selected:
        print("No live ADB device found. Recover USB or Wi-Fi ADB first.")
        return 1

    print_header("Expose OpenClaw To Termux")
    result = adb_on(selected, "reverse", f"tcp:{PROXY_PORT}", f"tcp:{PROXY_PORT}")
    output = (result.stdout or result.stderr).strip()
    if output:
        print(output)
    print(f"Device localhost:{PROXY_PORT} now points to PC localhost:{PROXY_PORT}")
    print()
    print_termux_proxy_exports()
    return 0 if result.returncode == 0 else 1


def print_termux_proxy_plan():
    print_header("Termux + OpenClaw Plan")
    print("Use this when the phone is attached by USB ADB or ADB over Wi-Fi:")
    print()
    print(f"1. Verify the PC proxy: {PROXY_HEALTH_URL}")
    print(f"2. Reverse the port: adb reverse tcp:{PROXY_PORT} tcp:{PROXY_PORT}")
    print("3. Open Termux on the phone.")
    print("4. Inside Termux, point OpenAI-compatible tools at the reversed localhost URL.")
    print()
    print_termux_proxy_exports()
    print()
    print("Important routing note:")
    print(
        "- because the manager is intentionally bound to PC localhost, the phone should"
    )
    print("  reach it through adb reverse, not through the PC LAN IP.")


def print_bootstrap_plan():
    print_header("Termux Bootstrap Plan")
    print("Once ADB is live and Termux opens, use this as the first Linux path:")
    print()
    print("Inside Termux:")
    print("pkg update && pkg upgrade -y")
    print("pkg install openssh termux-services -y")
    print("termux-setup-storage")
    print("passwd")
    print("sv-enable sshd")
    print("sshd")
    print()
    print("Then from the PC, choose one of these access paths:")
    print(f"- USB ADB tunnel: adb forward tcp:{SSHD_PORT} tcp:{SSHD_PORT}")
    print(f"  ssh -p {SSHD_PORT} <termux-user>@127.0.0.1")
    print(f"- Wi-Fi direct:   ssh -p {SSHD_PORT} <termux-user>@<phone_ip>")
    print()
    print("Optional next step if you want GUI or distro tooling:")
    print("- open Termux:X11 if installed")
    print("- verify Andronix / Linux Deploy state")
    print("- decide whether the stable remote path should be Wi-Fi ADB or SSH")
    print()
    print("Practical rule:")
    print("- use ADB to recover, launch, and forward ports")
    print("- use SSH to actually work inside Termux/Linux")
    print()
    print("To reach the PC-side Antigravity/OpenClaw proxy from Termux:")
    print(f"- keep the PC manager on localhost:{PROXY_PORT}")
    print(f"- run: adb reverse tcp:{PROXY_PORT} tcp:{PROXY_PORT}")
    print(f"- then use: {PROXY_BASE_URL}")
    print()
    print("If you later install/use Termux:Boot, the usual direction is:")
    print("#!/data/data/com.termux/files/usr/bin/sh")
    print("termux-wake-lock")
    print("source /data/data/com.termux/files/usr/etc/profile.d/start-services.sh")
    print("sshd")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Bridge Note9 ADB -> Wi-Fi ADB -> Termux/Linux launch flow."
    )
    parser.add_argument(
        "--ip",
        default=LAST_KNOWN_WIFI_IP,
        help=f"Wi-Fi ADB hint. Default: {LAST_KNOWN_WIFI_IP}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show current ADB and Termux/Linux state.")
    subparsers.add_parser("wifi", help="Promote USB ADB to Wi-Fi ADB or try direct connect.")
    subparsers.add_parser(
        "prepare-termux",
        help="Enable Termux external app execution and copy Debian launchers into Termux home.",
    )
    subparsers.add_parser("forward-ssh", help="Forward local port 8022 to Termux sshd over ADB.")
    subparsers.add_parser(
        "reverse-openclaw",
        help="Expose the local Antigravity/OpenClaw proxy to the phone with adb reverse.",
    )
    subparsers.add_parser(
        "open-debian",
        help="Open the Debian CLI launcher inside Termux.",
    )
    subparsers.add_parser(
        "open-xfce",
        help="Open the Debian XFCE launcher inside Termux and Termux:X11.",
    )
    launch_parser = subparsers.add_parser("launch", help="Launch a Linux-related Android app.")
    launch_parser.add_argument("app", choices=sorted(PACKAGE_MAP.keys()))
    termux_run = subparsers.add_parser(
        "termux-run",
        help="Send a simple command to the active Termux session via adb input.",
    )
    termux_run.add_argument("termux_command", nargs=argparse.REMAINDER)
    subparsers.add_parser("bootstrap-plan", help="Print the recommended Termux bootstrap plan.")
    subparsers.add_parser(
        "proxy-plan",
        help="Print the Termux/OpenClaw proxy plan and environment variables.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        return show_status(args.ip)
    if args.command == "wifi":
        return connect_wifi(args.ip)
    if args.command == "prepare-termux":
        return prepare_termux(args.ip)
    if args.command == "launch":
        return launch_app(args.app, args.ip)
    if args.command in LAUNCHER_MAP:
        return open_termux_target(args.command, args.ip)
    if args.command == "termux-run":
        return run_termux_command(args.termux_command, args.ip)
    if args.command == "forward-ssh":
        return forward_ssh(args.ip)
    if args.command == "reverse-openclaw":
        return reverse_openclaw(args.ip)
    if args.command == "bootstrap-plan":
        print_bootstrap_plan()
        return 0
    if args.command == "proxy-plan":
        print_termux_proxy_plan()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
