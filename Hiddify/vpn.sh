#!/bin/bash
# Usage: vpn.sh [extra args passed to check_submissions]
CONFIG=/home/mrn/hours/Hiddify/config.txt
PROXY=http://127.0.0.1:2334

cleanup() {
if kill -0 $VPN_PID 2>/dev/null; then
kill $VPN_PID
fi
}

trap cleanup EXIT

HiddifyCli run -c "$CONFIG" &
VPN_PID=$!

# wait until the tunnel actually carries traffic instead of hoping after 5s
for i in $(seq 30); do
	if curl -s --max-time 5 --proxy "$PROXY" -o /dev/null https://api.telegram.org; then
		break
	fi
	sleep 2
done

if ! curl -s --max-time 5 --proxy "$PROXY" -o /dev/null https://api.telegram.org; then
	echo "VPN never came up - aborting, not running check_submissions" >&2
	exit 1
fi

cd /home/mrn/hours/hours
/home/mrn/hours/venv/bin/python manage.py check_submissions "$@"
