#!/bin/bash
# Sauvegarde quotidienne de la base SQLite (copie cohérente) et des médias.
# Planification : crontab -e  ->  0 2 * * * /srv/fermegest/deploy/sauvegarde.sh
set -e
DEST=/var/backups/fermegest
mkdir -p "$DEST"
DATE=$(date +%F)
sqlite3 /srv/fermegest/db.sqlite3 ".backup '$DEST/db-$DATE.sqlite3'"
tar czf "$DEST/media-$DATE.tar.gz" -C /srv/fermegest media
find "$DEST" -type f -mtime +30 -delete    # conservation : 30 jours
