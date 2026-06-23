#!/bin/bash
#
# Tiered SQLite backup for the ESFA hours app.
#
# Runs once per day (via esfa_backup.timer) and keeps a grandfather-father-son
# rotation of compressed backups:
#
#   daily/    last 3 days        (DAILY_KEEP)
#   weekly/   last ~4 weeks      (WEEKLY_KEEP)  -> covers "last week"
#   monthly/  last 3 months      (MONTHLY_KEEP) -> covers "last month" + "3 last months"
#
# The backup is taken with sqlite3's online ".backup" command, which is safe
# to run while the web app is live (it does not lock writers out / corrupt).

set -euo pipefail

# --- config -----------------------------------------------------------------
DB="${ESFA_DB_PATH:-/home/mrn/hours/hours/db.sqlite3}"
BACKUP_ROOT="${ESFA_BACKUP_DIR:-/home/mrn/hours/backups}"

DAILY_KEEP=3
WEEKLY_KEEP=4
MONTHLY_KEEP=3
# ----------------------------------------------------------------------------

if [[ ! -f "$DB" ]]; then
    echo "ERROR: database not found at $DB" >&2
    exit 1
fi

stamp="$(date +%Y-%m-%d_%H%M%S)"
day_of_week="$(date +%u)"   # 1 = Monday
day_of_month="$(date +%d)"

daily_dir="$BACKUP_ROOT/daily"
weekly_dir="$BACKUP_ROOT/weekly"
monthly_dir="$BACKUP_ROOT/monthly"
mkdir -p "$daily_dir" "$weekly_dir" "$monthly_dir"

# --- take a consistent snapshot ---------------------------------------------
tmp_db="$(mktemp --suffix=.sqlite3)"
trap 'rm -f "$tmp_db"' EXIT

# .backup copies a transactionally-consistent image even under concurrent use.
sqlite3 "$DB" ".backup '$tmp_db'"
# Integrity check before we trust this snapshot.
if [[ "$(sqlite3 "$tmp_db" 'PRAGMA integrity_check;')" != "ok" ]]; then
    echo "ERROR: integrity check failed on snapshot" >&2
    exit 1
fi

daily_file="$daily_dir/db_${stamp}.sqlite3.gz"
gzip -c "$tmp_db" > "$daily_file"
echo "wrote $daily_file ($(du -h "$daily_file" | cut -f1))"

# --- promote into weekly / monthly tiers ------------------------------------
# Weekly: take one on Mondays (or if none exists yet this run-week).
if [[ "$day_of_week" == "1" ]] || ! ls "$weekly_dir"/db_"$(date +%Y-%m-%d)"*.gz >/dev/null 2>&1 && [[ -z "$(find "$weekly_dir" -name '*.gz' -mtime -6 2>/dev/null)" ]]; then
    cp "$daily_file" "$weekly_dir/db_${stamp}.sqlite3.gz"
    echo "promoted to weekly"
fi

# Monthly: take one on the 1st (or if none exists in the last ~27 days).
if [[ "$day_of_month" == "01" ]] || [[ -z "$(find "$monthly_dir" -name '*.gz' -mtime -27 2>/dev/null)" ]]; then
    cp "$daily_file" "$monthly_dir/db_${stamp}.sqlite3.gz"
    echo "promoted to monthly"
fi

# --- prune each tier --------------------------------------------------------
prune() {
    local dir="$1" keep="$2"
    # List newest-first, skip the first $keep, delete the rest.
    ls -1t "$dir"/*.gz 2>/dev/null | tail -n +"$((keep + 1))" | while read -r old; do
        rm -f "$old"
        echo "pruned $old"
    done
}

prune "$daily_dir"   "$DAILY_KEEP"
prune "$weekly_dir"  "$WEEKLY_KEEP"
prune "$monthly_dir" "$MONTHLY_KEEP"

echo "backup complete: $(date)"
