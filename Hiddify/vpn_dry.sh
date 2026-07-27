cleanup() {
if kill -0 $VPN_PID 2>/dev/null; then
kill $VPN_PID
fi
}

trap cleanup EXIT

HiddifyCli run -c https://raw.githubusercontent.com/hiddify/hiddify-app/refs/heads/main/test.configs/mahsa#Mahsa &
VPN_PID=$!

sleep 5

cd /home/mrn/hours/hours
/home/mrn/hours/venv/bin/python manage.py check_submissions --dry-run

exit 0