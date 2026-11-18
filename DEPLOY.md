# Deploying "hours" (hours.esfagroup.com)

Server: **esfagroup-01**, user `deploy` (uid 1000), checkout in `/opt/hours`. The app is a Docker container (gunicorn + Django, port 8000) behind the shared **nginx-proxy + acme-companion** stack in `/opt/proxy` (Docker network `proxy`), which also gets the Let's Encrypt certificate. The site lives at the **root** of the domain (no `/hours/` prefix). The old address `kavosh.online/hours/...` is redirected here by the Kavosh nginx config (kavosh repo, `deploy/nginx-vhost.conf`).

The Telegram checker and the SQLite backups run on the host (systemd timers). The checker goes through the host's Hiddify VPN, because Telegram is not reachable directly from the server.

```
/opt/hours/                            (git checkout)
├── Dockerfile, docker-compose.yml     (from git)
├── .env                               NOT in git: HOURS_DOMAIN etc. (from .env.example)
├── data/                              NOT in git: all state lives here
│   ├── db.sqlite3
│   ├── media/
│   ├── error.log
│   └── local.py                       production settings and secrets (mounted read-only)
└── backups/                           written by the backup timer
```

---

## 1. Prepare the server (once, needs sudo)

```bash
sudo install -d -o deploy -g deploy /opt/hours
sudo apt-get install -y sqlite3                    # used by system_files/db_backup.sh
sudo install -m 755 HiddifyCli /usr/local/bin/      # Hiddify CLI binary (only needed for Telegram alerts)
```

The `proxy` network must already exist (`/opt/proxy`).

## 2. Get the code

```bash
git clone <repo-url> /opt/hours      # or from a git bundle
cd /opt/hours
mkdir -p data/media backups
cp .env.example .env && chmod 600 .env
```

## 3. Bring the data

**Moving from another server** (stop the old app first, so nothing writes while you copy):

```bash
# on the OLD server: consistent DB snapshot (safe even if the app is running)
sqlite3 <old>/db.sqlite3 ".backup /tmp/db.sqlite3"
# copy to /opt/hours/data/db.sqlite3 and the media folder to /opt/hours/data/media/
```

**Fresh install with no data:** skip the copy. The container creates an empty DB on first start; then create an admin with:
`docker compose exec web python manage.py createsuperuser`.

## 4. Production settings: `data/local.py`

Never committed. Generate a key with `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`.

```python
SECRET_KEY = "<generated key>"
DEBUG = False
ALLOWED_HOSTS = ["hours.esfagroup.com"]
CSRF_TRUSTED_ORIGINS = ["https://hours.esfagroup.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")   # nginx-proxy sends this header

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/data/db.sqlite3"}}
MEDIA_ROOT = "/data/media/"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"f": {"level": "ERROR", "class": "logging.FileHandler", "filename": "/data/error.log"}},
    "loggers": {"django": {"handlers": ["f"], "level": "ERROR", "propagate": True}},
}
```

Then make `data/` writable by the container user (uid 1000 = `deploy`):

```bash
chown -R 1000:1000 data && chmod 600 data/local.py .env
```

## 5. nginx-proxy settings for this host

Uploads (photos, Excel) and slow imports need more than nginx's defaults (1 MB, 60 s). `vhost.d` is a volume of the proxy stack, so this survives restarts:

```bash
docker exec nginx-proxy sh -c 'printf "client_max_body_size 50m;\nproxy_read_timeout 300s;\n" > /etc/nginx/vhost.d/hours.esfagroup.com'
docker exec nginx-proxy nginx -s reload
```

nginx-proxy only picks up a new `vhost.d/<host>` file when it regenerates its config (on container start/stop events), so create it **before** the first `docker compose up`, or `docker compose restart web` afterwards.

Do **not** add a `location /media/` alias: media goes through Django's `MediaServeView`, which keeps personal documents (ID cards, ...) private to their owner and staff. Static files are served by WhiteNoise inside the container.

## 6. Image, build and start

Docker Hub is blocked from esfagroup-01, so either build elsewhere and ship the image:

```bash
docker compose build web
docker save hours:latest | gzip | ssh esfagroup-01 'gunzip | docker load'
```

or set `BASE_IMAGE` in `.env` to a mirror (e.g. `docker.arvancloud.ir/python:3.12-slim`) and build on the server. Then:

```bash
docker compose up -d                 # add --build when building on the server
docker compose logs -f web           # expect "Listening at: http://0.0.0.0:8000"
```

On every start the container runs `migrate`, then gunicorn (3 workers, 300 s timeout). acme-companion requests the certificate on first start (DNS must already point here). `restart: unless-stopped` brings it back after reboots.

## 7. Scheduled jobs (host systemd, needs sudo)

```bash
cd /opt/hours/system_files
sudo cp esfa_backup.service esfa_backup.timer esfa_checker.service esfa_checker.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now esfa_backup.timer esfa_checker.timer
```

| Timer | When | What |
|---|---|---|
| `esfa_backup` | daily 02:30 | tiered gzip backups of `data/db.sqlite3` into `backups/{daily,weekly,monthly}` |
| `esfa_checker` | every 4 h | starts the VPN, then runs `check_submissions` in a one-off `checker` container on the host network |

Test both once by hand:

```bash
sudo systemctl start esfa_backup.service && ls backups/daily     # a new .gz appears
sudo /opt/hours/Hiddify/vpn_dry.sh                               # dry run, no messages sent
```

## 8. Smoke test

- Open `https://hours.esfagroup.com/` and log in.
- Open a month sheet (static files and the API work).
- View a user's uploaded photo (media through Django).
- Run a small Excel import (background task and status polling).
- `https://kavosh.online/hours/home` redirects to `https://hours.esfagroup.com/home`.
- `docker compose logs web` and `data/error.log` have no errors.

---

## Day-to-day

```bash
# update the app
cd /opt/hours && git pull
# rebuild (or build + ship, section 6), then:
docker compose up -d

# logs / shell / manage.py
docker compose logs -f web
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser

# restart / stop
docker compose restart web
docker compose down
```

**Rollback:** `git checkout <previous-commit>`, rebuild, `docker compose up -d`. Migrations that already ran are not undone, so restore a DB backup too if the release changed the schema.

**Restore a backup:**

```bash
docker compose stop web
gunzip -c backups/daily/db_<stamp>.sqlite3.gz > data/db.sqlite3
chown 1000:1000 data/db.sqlite3
docker compose start web
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `pull access denied` / timeout on build | Docker Hub unreachable: ship the image or use `BASE_IMAGE` with a mirror (section 6) |
| Container exits at once | `docker compose logs web`; usually a bad `data/local.py` or an unwritable `data/` |
| 400 Bad Request | domain missing from `ALLOWED_HOSTS` |
| 403 CSRF failed on login | `CSRF_TRUSTED_ORIGINS` or `SECURE_PROXY_SSL_HEADER` missing in `data/local.py` |
| 502 / 503 from nginx-proxy | container not running or not on the `proxy` network; for 503 also check `HOURS_DOMAIN` in `.env` |
| No certificate / browser warning | DNS did not point here when the container started; `docker logs nginx-proxy-acme`, then `docker compose restart web` |
| 413 on upload | the `vhost.d/hours.esfagroup.com` file from section 5 is missing |
| Telegram alerts never arrive | Hiddify not running or no `HiddifyCli` on root's PATH; run `vpn_dry.sh` by hand |
| "Dry run via VPN" button in the UI fails | expected: HiddifyCli runs on the host, not in the container; use the plain dry run or run `vpn_dry.sh` on the host |

## Security notes

- The repo still contains secrets in plain text: the old server's SSH password (`hours/fetch-db-from-server.sh`), the Telegram bot token (`check_submissions.py`) and the brsapi key (`esfa_eyes/api_views.py`). Rotate them, and move them to `data/local.py` when you can.
- `Hiddify/config.txt` holds your VPN credentials. Don't make the repo public.
- Back up `data/` (especially `local.py`) off the server. The timer's backups only live on the same disk.
