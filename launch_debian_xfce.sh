#!/data/data/com.termux/files/usr/bin/bash

set -e

export PATH=/data/data/com.termux/files/usr/bin:$PATH
export PREFIX=/data/data/com.termux/files/usr
export HOME=/data/data/com.termux/files/home
export TMPDIR=/data/data/com.termux/files/usr/tmp
export XDG_RUNTIME_DIR="$TMPDIR"

mkdir -p "$TMPDIR"

pkill -f "termux.x11" 2>/dev/null || true

if ! pulseaudio --check 2>/dev/null; then
  pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1
fi

termux-x11 :0 >/dev/null 2>&1 &
sleep 3

am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1 || true
sleep 1

exec /data/data/com.termux/files/usr/bin/proot-distro login debian --shared-tmp -- /bin/bash -lc '
install -d -m 700 -o 1000 -g 1000 /tmp/runtime-zerausn
su - zerausn -c "export DISPLAY=:0 PULSE_SERVER=127.0.0.1 XDG_RUNTIME_DIR=/tmp/runtime-zerausn; exec dbus-launch --exit-with-session startxfce4"
'
