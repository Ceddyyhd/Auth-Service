# Auth-Service Deployment Dokumentation

## Server-Anforderungen

- **OS:** Debian 12 (Bookworm)
- **RAM:** Mindestens 2 GB (4 GB empfohlen)
- **CPU:** Mindestens 2 Cores
- **Storage:** Mindestens 20 GB
- **Domain:** auth.palmdynamicx.de (DNS muss auf Server-IP zeigen)

---

## Deployment-Prozess

### Schritt 1: Server vorbereiten

```bash
# SSH-Zugriff zum Server
ssh root@your-server-ip

# System updaten
apt update && apt upgrade -y
```

---

### Schritt 2: DNS konfigurieren

Stelle sicher, dass die Domain auf deinen Server zeigt:

**A-Record:**
```
auth.palmdynamicx.de  →  YOUR_SERVER_IP
www.auth.palmdynamicx.de  →  YOUR_SERVER_IP
```

**Prüfen:**
```bash
dig auth.palmdynamicx.de
nslookup auth.palmdynamicx.de
```

---

### Schritt 3: Deployment-Script hochladen

**Von deinem lokalen Rechner:**

```bash
# Script zum Server kopieren
scp deploy.sh root@your-server-ip:/root/

# Ausführbar machen
ssh root@your-server-ip "chmod +x /root/deploy.sh"
```

---

### Schritt 4: Code zum Server kopieren

**Option A: Mit rsync (empfohlen)**

```bash
# Aus dem Projekt-Verzeichnis
rsync -avz --progress \
  --exclude='venv' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.sqlite3' \
  --exclude='db.sqlite3' \
  --exclude='node_modules' \
  ./ root@your-server-ip:/var/www/auth-service/
```

**Option B: Mit Git**

```bash
ssh root@your-server-ip
cd /var/www
git clone https://github.com/your-repo/auth-service.git
cd auth-service
```

---

### Schritt 5: Deployment-Script ausführen

```bash
ssh root@your-server-ip

# Script ausführen
cd /root
./deploy.sh
```

Das Script wird:
1. ✅ Alle Dependencies installieren (Python, PostgreSQL, Redis, NGINX)
2. ✅ PostgreSQL-Datenbank einrichten
3. ✅ Python Virtual Environment erstellen
4. ✅ Django konfigurieren
5. ✅ Gunicorn als Systemd Service einrichten
6. ✅ NGINX als Reverse Proxy konfigurieren

**Während der Ausführung:**
- Du wirst aufgefordert, einen Django Superuser zu erstellen
- Notiere die Datenbank-Credentials (werden angezeigt)

---

### Schritt 6: SSL-Zertifikat installieren

```bash
# Let's Encrypt Zertifikat holen
certbot --nginx -d auth.palmdynamicx.de -d www.auth.palmdynamicx.de

# Folge den Anweisungen:
# - Email-Adresse eingeben
# - Terms akzeptieren
# - Redirect von HTTP zu HTTPS wählen (empfohlen)
```

**Auto-Renewal testen:**
```bash
certbot renew --dry-run
```

---

### Schritt 7: Firewall konfigurieren

```bash
# UFW installieren (falls nicht vorhanden)
apt install ufw

# Regeln setzen
ufw allow OpenSSH
ufw allow 'Nginx Full'

# Firewall aktivieren
ufw enable

# Status prüfen
ufw status
```

---

### Schritt 8: Finale Tests

#### Test 1: API erreichbar?

```bash
curl https://auth.palmdynamicx.de/api/schema/
```

**Erwartete Ausgabe:** JSON mit API-Schema

#### Test 2: Admin-Panel

Browser öffnen: `https://auth.palmdynamicx.de/admin/`

Mit dem erstellten Superuser anmelden.

#### Test 3: Health Check

```bash
curl https://auth.palmdynamicx.de/
```

---

## Service-Verwaltung

### Gunicorn Service

```bash
# Status prüfen
systemctl status authservice

# Neustarten
systemctl restart authservice

# Stoppen
systemctl stop authservice

# Starten
systemctl start authservice

# Logs ansehen (Live)
journalctl -u authservice -f

# Logs ansehen (letzte 100 Zeilen)
journalctl -u authservice -n 100
```

### NGINX

```bash
# Status
systemctl status nginx

# Neustarten
systemctl restart nginx

# Config testen
nginx -t

# Reload (ohne Downtime)
systemctl reload nginx

# Access Logs
tail -f /var/log/nginx/access.log

# Error Logs
tail -f /var/log/nginx/error.log
```

### PostgreSQL

```bash
# Status
systemctl status postgresql

# Als postgres-User verbinden
sudo -u postgres psql

# Datenbank-Backup
sudo -u postgres pg_dump auth_service_db > backup.sql

# Backup wiederherstellen
sudo -u postgres psql auth_service_db < backup.sql
```

### Redis

```bash
# Status
systemctl status redis-server

# Redis CLI
redis-cli

# Alle Keys anzeigen
redis-cli KEYS '*'

# Cache leeren
redis-cli FLUSHALL
```

---

## Wichtige Dateien & Verzeichnisse

```
/var/www/auth-service/          # App-Verzeichnis
├── .env                        # Umgebungsvariablen (GEHEIM!)
├── manage.py                   # Django Management
├── auth_service/               # Django Projekt
├── accounts/                   # Accounts App
├── permissions_system/         # Permissions App
├── venv/                       # Virtual Environment
└── staticfiles/                # Gesammelte Static Files

/etc/nginx/
├── sites-available/authservice # NGINX Config
└── sites-enabled/authservice   # Symlink zur Config

/etc/systemd/system/
├── authservice.service         # Gunicorn Service
└── authservice.socket          # Gunicorn Socket

/var/log/authservice/           # Application Logs
├── access.log                  # Gunicorn Access Log
└── error.log                   # Gunicorn Error Log

/root/.auth_service_db_creds    # Datenbank-Credentials (BACKUP!)
```

---

## Konfiguration nach Deployment

### 1. Email-Einstellungen (.env)

```bash
nano /var/www/auth-service/.env
```

Aktualisiere:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@palmdynamicx.de
```

Danach Neustart:
```bash
systemctl restart authservice
```

---

### 2. Erste Website registrieren

```bash
# Django Shell öffnen
cd /var/www/auth-service
source venv/bin/activate
python manage.py shell
```

```python
from accounts.models import Website

# Website erstellen
website = Website.objects.create(
    name="Website A",
    domain="website-a.palmdynamicx.de",
    allowed_origins="https://website-a.palmdynamicx.de"
)

# API Credentials generieren
website.generate_credentials()
website.save()

# Credentials anzeigen
print(f"API Key: {website.api_key}")
print(f"API Secret: {website.api_secret}")
print(f"Website ID: {website.id}")
```

---

### 3. CORS für Frontend

Bearbeite `/var/www/auth-service/.env`:

```env
CORS_ALLOWED_ORIGINS=https://auth.palmdynamicx.de,https://website-a.palmdynamicx.de,https://website-b.palmdynamicx.de
```

Neustart:
```bash
systemctl restart authservice
```

---

## Monitoring & Wartung

### Log-Rotation einrichten

```bash
# Log-Rotation Config erstellen
cat > /etc/logrotate.d/authservice <<EOF
/var/log/authservice/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 authservice authservice
    sharedscripts
    postrotate
        systemctl reload authservice > /dev/null
    endscript
}
EOF
```

---

### Backup-Script erstellen

```bash
cat > /root/backup-authservice.sh <<'EOF'
#!/bin/bash

BACKUP_DIR="/root/backups/auth-service"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Datenbank Backup
sudo -u postgres pg_dump auth_service_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# .env Backup
cp /var/www/auth-service/.env $BACKUP_DIR/env_$DATE

# Media Files Backup (falls vorhanden)
# tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/auth-service/media/

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup-authservice.sh
```

**Cronjob für tägliches Backup:**
```bash
crontab -e

# Jeden Tag um 2 Uhr morgens
0 2 * * * /root/backup-authservice.sh >> /var/log/auth-backup.log 2>&1
```

---

### Performance-Monitoring

**1. Resource-Nutzung prüfen:**
```bash
# CPU & RAM
htop

# Disk-Space
df -h

# Netzwerk
iftop
```

**2. Application-Performance:**
```bash
# Gunicorn Worker Status
systemctl status authservice

# Anzahl Requests
tail -f /var/log/authservice/access.log | grep -c "GET"

# Response Times
tail -f /var/log/authservice/access.log
```

**3. Datenbank-Performance:**
```bash
sudo -u postgres psql auth_service_db

# Langsame Queries finden
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Troubleshooting

### Problem: Service startet nicht

```bash
# Detaillierte Logs
journalctl -u authservice -xe

# Häufige Ursachen:
# 1. .env fehlt oder falsch
cat /var/www/auth-service/.env

# 2. Datenbank nicht erreichbar
sudo -u postgres psql -l

# 3. Port bereits belegt
ss -tulpn | grep 8000

# 4. Permissions
ls -la /var/www/auth-service/
```

---

### Problem: 502 Bad Gateway

```bash
# NGINX Error Log
tail -f /var/log/nginx/error.log

# Gunicorn läuft?
systemctl status authservice

# Socket vorhanden?
ls -la /run/authservice.sock

# NGINX Config testen
nginx -t

# Neustart
systemctl restart authservice
systemctl restart nginx
```

---

### Problem: Static Files nicht geladen

```bash
# Static Files neu sammeln
cd /var/www/auth-service
source venv/bin/activate
python manage.py collectstatic --clear --noinput

# Permissions prüfen
chown -R authservice:www-data /var/www/auth-service/staticfiles/
chmod -R 755 /var/www/auth-service/staticfiles/

# NGINX Neustart
systemctl restart nginx
```

---

### Problem: Datenbank-Verbindung fehlgeschlagen

```bash
# PostgreSQL läuft?
systemctl status postgresql

# Credentials prüfen
cat /root/.auth_service_db_creds

# Als postgres-User testen
sudo -u postgres psql auth_service_db

# .env prüfen
cat /var/www/auth-service/.env | grep DB_
```

---

### Problem: SSL-Zertifikat abgelaufen

```bash
# Zertifikat-Status
certbot certificates

# Manuell erneuern
certbot renew

# Auto-Renewal testen
certbot renew --dry-run
```

---

## Updates & Wartung

### Code-Update deployen

```bash
# 1. Code zum Server syncen
rsync -avz --exclude='venv' --exclude='*.pyc' ./ root@your-server-ip:/var/www/auth-service/

# 2. Auf Server
ssh root@your-server-ip

# 3. Als authservice-User
sudo -u authservice bash
cd /var/www/auth-service
source venv/bin/activate

# 4. Dependencies updaten
pip install -r requirements.txt

# 5. Migrationen
python manage.py migrate

# 6. Static Files
python manage.py collectstatic --noinput

# 7. Service neustarten
exit  # Zurück zu root
systemctl restart authservice
```

---

### Python-Packages updaten

```bash
sudo -u authservice bash
cd /var/www/auth-service
source venv/bin/activate

# Alle Packages auflisten
pip list --outdated

# Einzelnes Package updaten
pip install --upgrade django

# requirements.txt updaten
pip freeze > requirements.txt

# Service neustarten
exit
systemctl restart authservice
```

---

## Security Best Practices

### 1. Firewall

```bash
# Nur notwendige Ports öffnen
ufw status numbered
ufw delete <nummer>  # Ungenutzte Ports schließen
```

### 2. SSH Hardening

```bash
nano /etc/ssh/sshd_config

# Ändern:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

systemctl restart sshd
```

### 3. Fail2Ban installieren

```bash
apt install fail2ban

# NGINX-Jail aktivieren
cat > /etc/fail2ban/jail.local <<EOF
[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
EOF

systemctl restart fail2ban
```

### 4. Regelmäßige Updates

```bash
# Auto-Updates aktivieren
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## Performance-Optimierung

### 1. Gunicorn Workers anpassen

```bash
nano /etc/systemd/system/authservice.service

# Formel: (2 × CPU_CORES) + 1
# Bei 4 Cores: --workers 9

systemctl daemon-reload
systemctl restart authservice
```

### 2. PostgreSQL tunen

```bash
nano /etc/postgresql/15/main/postgresql.conf

# Für 4GB RAM:
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
work_mem = 16MB

systemctl restart postgresql
```

### 3. Redis als Cache nutzen

Bereits konfiguriert in `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

---

## Kontakt & Support

Bei Problemen:
1. Logs prüfen: `journalctl -u authservice -f`
2. NGINX-Logs: `tail -f /var/log/nginx/error.log`
3. Service-Status: `systemctl status authservice nginx postgresql redis-server`

---

**Deployment abgeschlossen!** 🎉

Dein Auth-Service läuft jetzt auf: `https://auth.palmdynamicx.de`
