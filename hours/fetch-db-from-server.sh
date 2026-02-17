#!/bin/bash

# Simple SQLite Database Download Script
SERVER_IP="185.211.58.47"
SERVER_USER="mrn"
DB_PATH="/home/mrn/hours/hours/db.sqlite3"

# Create backup with timestamp
timestamp=$(date +%Y%m%d_%H%M%S)
backup_file="db_backup_${timestamp}.sqlite3"

echo -n "Enter SSH password: "
read -s SERVER_PASSWORD
echo

echo "Downloading database..."

# Download the SQLite database directly
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_IP}:${DB_PATH}" \
    "./${backup_file}"

chmod 664 "$backup_file"
chown $USER:$USER "$backup_file"

echo "Database downloaded: ${backup_file}"

# If you want to replace the existing db.sqlite3 file, uncomment the following lines:
# sudo chmod 664 db.sqlite3
# sudo chown $USER:$USER db.sqlite3