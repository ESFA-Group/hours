#!/bin/bash
# Download a consistent snapshot of the production SQLite database.
# Uses the "esfagroup-01" alias from ~/.ssh/config (key-based login, no password).
# Run from the hours/ directory; the backup is saved next to this script.
set -euo pipefail

SERVER="esfagroup-01"
DB_PATH="/opt/hours/data/db.sqlite3"
REMOTE_TMP="/tmp/db_snapshot_$$.sqlite3"

cd "$(dirname "$0")"

timestamp=$(date +%Y%m%d_%H%M%S)
backup_file="db_backup_${timestamp}.sqlite3"

echo "Creating snapshot on server..."
# .backup is safe while the app is running (a plain file copy could catch a write)
ssh "$SERVER" "sqlite3 '$DB_PATH' \".backup '$REMOTE_TMP'\""

echo "Downloading database..."
scp "$SERVER:$REMOTE_TMP" "./${backup_file}"

# The database holds personal data: don't leave the snapshot on the server
ssh "$SERVER" "rm -f '$REMOTE_TMP'"

chmod 664 "$backup_file"

echo "Database downloaded: ${backup_file}"

# To use it as your local database, uncomment:
# cp "$backup_file" db.sqlite3
