#!/data/data/com.termux/files/usr/bin/bash

set -e

export PATH=/data/data/com.termux/files/usr/bin:$PATH
export PREFIX=/data/data/com.termux/files/usr
export HOME=/data/data/com.termux/files/home
export TMPDIR=/data/data/com.termux/files/usr/tmp

mkdir -p "$TMPDIR"

exec /data/data/com.termux/files/usr/bin/proot-distro login debian --shared-tmp -- /bin/bash -lc '
export OPENAI_BASE_URL=http://127.0.0.1:8045/v1
export OPENAI_API_KEY=sk-antigravity
cd /root
exec openclaw tui
'
