# Deploying "hours" on a new server

Stack: Docker (gunicorn + Django) behind the **host's nginx**. The Telegram checker and the SQLite backups run on the host (systemd timers) and use the host's Hiddify VPN.

All paths below assume the server user is `mrn` (uid 1000) and the repo lives in `/home/mrn/hours`. If your user differs, change `user:` in `docker-compose.yml` and the paths in `system_files/*.service`.

```
/home/mrn/hours/
├── Dockerfile, docker-compose.yml     (from git)
├── data/                              (NOT in git: all state lives here)
│   ├── db.sqlite3
│   ├── media/
│   ├── error.log
│   └── local.py                       (production settings and secrets)
└── backups/                           (written by the backup timer)
```

---

## 1. Prepare the server

```bash
# base packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y git nginx sqlite3 curl docker.io docker-compose-v2
sudo usermod -aG docker mrn            # log out and back in afterwards
docker --version && docker compose version
```

**Docker Hub blocked / slow (common in Iran):** turn on the VPN, or add a registry mirror and restart Docker:

```bash
echo '{"registry-mirrors": ["https://docker.arvancloud.ir"]}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

**Hiddify (only needed for Telegram alerts):** install `HiddifyCli` so it's on root's `PATH` (e.g. `/usr/local/bin/HiddifyCli`). The checker timer runs as root. Test it:

```bash
HiddifyCli run -c /home/mrn/hours/Hiddify/config.txt &   # then, in another shell:
curl --proxy http://127.0.0.1:2334 -I https://api.telegram.org
```

## 2. Get the code

```bash
cd /home/mrn
git clone <repo-url> hours
cd hours
mkdir -p data backups
```

## 3. Bring the data

**Moving from the old server** (stop the old app first, so nothing writes while you copy):

```bash
# on the OLD server: consistent DB snapshot (safe even if the app is running)
sqlite3 /home/mrn/hours/hours/db.sqlite3 ".backup /tmp/db.sqlite3"
# copy to the NEW server
scp /tmp/db.sqlite3 mrn@NEW:/home/mrn/hours/data/db.sqlite3
rsync -a /home/mrn/hours/hours/media/ mrn@NEW:/home/mrn/hours/data/media/
```

**Fresh install with no data:** skip the copy. The container creates an empty DB on first start; then create an admin with:
`docker compose exec web python manage.py createsuperuser`.

## 4. Production settings: `data/local.py`

This file is mounted into the container (read-only) and is never committed. Generate a key with
`python3 -c "import secrets; print(secrets.token_urlsafe(50))"`.

```python
SECRET_KEY = "<generated key>"
DEBUG = False
ALLOWED_HOSTS = ["your.domain", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["https://your.domain"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")   # needs the nginx header below

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/data/db.sqlite3"}}
MEDIA_ROOT = "/data/media/"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"f": {"level": "ERROR", "class": "logging.FileHandler", "filename": "/data/error.log"}},
    "loggers": {"django": {"handlers": ["f"], "level": "ERROR", "propagate": True}},
}
```

Then make `data/` writable by the container user (uid in `docker-compose.yml`, default 1000):

```bash
sudo chown -R 1000:1000 data
chmod 600 data/local.py
```

## 5. Build and start

```bash
docker compose up -d --build
docker compose logs -f web          # expect "Listening at: http://127.0.0.1:8000"
curl -I http://127.0.0.1:8000/hours/
```

On every start the container runs `migrate`, then gunicorn (3 workers, 300 s timeout, bound to `127.0.0.1:8000`). `restart: unless-stopped` brings it back after reboots, as long as Docker is enabled (`sudo systemctl enable docker`).

> If the port is already taken, the old gunicorn is still running. Stop it first: `sudo systemctl disable --now <old-service>`.

## 6. nginx

`/etc/nginx/sites-available/hours`:

```nginx
server {
    listen 80;
    server_name your.domain;
    client_max_body_size 50m;                    # photo / Excel uploads

    location /hours/media/ { alias /home/mrn/hours/data/media/; }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;                 # matches gunicorn --timeout
    }
}
```

`/static/` needs no separate block: WhiteNoise inside the container serves it.

```bash
sudo ln -s /etc/nginx/sites-available/hours /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
# HTTPS: sudo apt-get install -y certbot python3-certbot-nginx && sudo certbot --nginx -d your.domain
```

If nginx can't read the media directory, run `chmod o+x /home/mrn /home/mrn/hours /home/mrn/hours/data`.

## 7. Scheduled jobs (host systemd)

```bash
cd /home/mrn/hours/system_files
sudo cp esfa_backup.service esfa_backup.timer esfa_checker.service esfa_checker.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now esfa_backup.timer esfa_checker.timer
chmod +x /home/mrn/hours/Hiddify/vpn.sh /home/mrn/hours/Hiddify/vpn_dry.sh
```

| Timer | When | What |
|---|---|---|
| `esfa_backup` | daily 02:30 | tiered gzip backups of `data/db.sqlite3` into `backups/{daily,weekly,monthly}` |
| `esfa_checker` | every 4 h | starts the VPN, then runs `check_submissions` inside the container |

Test both once by hand:

```bash
sudo systemctl start esfa_backup.service && ls backups/daily     # a new .gz appears
/home/mrn/hours/Hiddify/vpn_dry.sh                               # dry run, no messages sent
```

## 8. Smoke test

- Open `https://your.domain/hours/` and log in.
- Open a month sheet (static files and the API work).
- View a user's uploaded photo (media via nginx).
- Run a small Excel import (background task and status polling).
- `docker compose logs web` and `data/error.log` have no errors.

---

## Day-to-day

```bash
# update the app
cd /home/mrn/hours && git pull && docker compose up -d --build

# logs / shell / manage.py
docker compose logs -f web
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser

# restart / stop
docker compose restart web
docker compose down
```

**Rollback:** `git checkout <previous-commit> && docker compose up -d --build`. Migrations that already ran are not undone, so restore a DB backup too if the release changed the schema.

**Restore a backup:**

```bash
docker compose stop web
gunzip -c backups/daily/db_<stamp>.sqlite3.gz > data/db.sqlite3
sudo chown 1000:1000 data/db.sqlite3
docker compose start web
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `pull access denied` / timeout on build | Docker Hub unreachable: use the VPN or a registry mirror (step 1) |
| Container exits at once | `docker compose logs web`; usually a bad `data/local.py` or an unwritable `data/` |
| `Address already in use` | old gunicorn still running on port 8000 |
| 400 Bad Request | domain missing from `ALLOWED_HOSTS` |
| 403 CSRF failed on login (HTTPS) | `CSRF_TRUSTED_ORIGINS` or the `X-Forwarded-Proto` header is missing |
| 502 from nginx | container not running, or gunicorn not on `127.0.0.1:8000` |
| Uploaded photos 404 | nginx `alias` path wrong, or `data/media` is not readable by nginx |
| Telegram alerts never arrive | Hiddify not running or no `HiddifyCli` on root's PATH; run `vpn_dry.sh` by hand |
| "Dry run via VPN" button in the UI fails | expected: HiddifyCli runs on the host, not in the container; use the plain dry run or run `vpn_dry.sh` on the host |

## Security notes

- The repo still contains secrets in plain text: the old server's SSH password (`hours/fetch-db-from-server.sh`), the Telegram bot token (`check_submissions.py`) and the brsapi key (`esfa_eyes/api_views.py`). Rotate them, and move them to `data/local.py` when you can.
- `Hiddify/config.txt` holds your VPN credentials. Don't make the repo public.
- Back up `data/` (especially `local.py`) off the server. The timer's backups only live on the same disk.
