cleanup() {
if kill -0 $VPN_PID 2>/dev/null; then
kill $VPN_PID
fi
}

trap cleanup EXIT

HiddifyCli run -c https://de11pooya.1qwertyuiopasdfghjklzxcvbnmmnbvcxzlkjhgfdsapoiuytrewq1234567890.com:2096/1qwertyuiopasdfghjklzxcvbnmmnbvcxzlkjhgfdsapoiuytrewq1234567890/ESFAGroup_2 &
VPN_PID=$!

sleep 5

cd /home/mrn/hours/hours
/home/mrn/hours/venv/bin/python manage.py check_submissions

exit 0