# 🚀 Deployment-Anleitung für auth.palmdynamicx.de

Diese Anleitung zeigt Ihnen, wie Sie den Auth Service auf `auth.palmdynamicx.de` deployen und für sichere Cross-Origin-API-Anfragen konfigurieren.

## 📋 Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Server-Setup](#server-setup)
- [Domain & SSL](#domain--ssl)
- [Datenbank-Konfiguration](#datenbank-konfiguration)
- [Umgebungsvariablen](#umgebungsvariablen)
- [Nginx-Konfiguration](#nginx-konfiguration)
- [Deployment](#deployment)
- [CORS für andere Websites](#cors-für-andere-websites)
- [API-Dokumentation aufrufen](#api-dokumentation-aufrufen)
- [Monitoring & Wartung](#monitoring--wartung)

---

## 🔧 Voraussetzungen

### Server-Anforderungen:
- **Ubuntu 22.04 LTS** oder höher
- **Python 3.10+**
- **PostgreSQL 14+**
- **Nginx** als Reverse Proxy
- **Supervisor** oder **systemd** für Process Management
- Mindestens **2 GB RAM**, **2 CPU Cores**, **20 GB Storage**

### Domain:
- Domain: `auth.palmdynamicx.de`
- SSL-Zertifikat (Let's Encrypt kostenlos)

---

## 🖥️ Server-Setup

### 1. Server aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python und Dependencies installieren

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip python3.11-dev
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y nginx supervisor git
```

### 3. PostgreSQL installieren

```bash
sudo apt install -y postgresql postgresql-contrib libpq-dev

# PostgreSQL starten
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4. Benutzer erstellen

```bash
# System-Benutzer für die Anwendung
sudo useradd -m -s /bin/bash palmdynamicx
sudo su - palmdynamicx
```

---

## 🗄️ Datenbank-Konfiguration

### PostgreSQL-Datenbank erstellen:

```bash
# Als postgres-User
sudo -u postgres psql

-- In der PostgreSQL-Shell:
CREATE DATABASE auth_service_db;
CREATE USER auth_service_user WITH PASSWORD 'IHR-SICHERES-PASSWORT-HIER';
GRANT ALL PRIVILEGES ON DATABASE auth_service_db TO auth_service_user;
ALTER USER auth_service_user CREATEDB;  -- Für Tests
\q
```

### PostgreSQL für Remote-Zugriff konfigurieren (optional):

```bash
# /etc/postgresql/14/main/postgresql.conf
listen_addresses = 'localhost'  # Nur lokaler Zugriff

# /etc/postgresql/14/main/pg_hba.conf
local   auth_service_db     auth_service_user                   md5
host    auth_service_db     auth_service_user   127.0.0.1/32    md5

sudo systemctl restart postgresql
```

---

## 🔐 Domain & SSL

### 1. DNS konfigurieren

Erstellen Sie einen A-Record bei Ihrem DNS-Provider:

```
Type: A
Name: auth
Value: <IHRE-SERVER-IP>
TTL: 3600
```

**Ergebnis:** `auth.palmdynamicx.de` → `<SERVER-IP>`

### 2. SSL-Zertifikat mit Let's Encrypt

```bash
# Certbot installieren
sudo apt install -y certbot python3-certbot-nginx

# Zertifikat generieren
sudo certbot --nginx -d auth.palmdynamicx.de

# Automatische Renewal einrichten
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test Renewal
sudo certbot renew --dry-run
```

---

## 📁 Deployment

### 1. Repository klonen

```bash
# Als palmdynamicx-User
cd /home/palmdynamicx
git clone https://github.com/IHR-REPO/Auth-Service.git
cd Auth-Service
```

### 2. Virtuelle Umgebung erstellen

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Umgebungsvariablen konfigurieren

Erstellen Sie `.env` Datei:

```bash
nano .env
```

**Inhalt der `.env` Datei:**

```bash
# ===========================
# DJANGO CORE
# ===========================
SECRET_KEY=ihr-sehr-langes-zufälliges-geheimnis-mindestens-50-zeichen-lang-generieren-mit-django
DEBUG=False
ALLOWED_HOSTS=auth.palmdynamicx.de,www.auth.palmdynamicx.de

# ===========================
# DATABASE (PostgreSQL)
# ===========================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=auth_service_db
DB_USER=auth_service_user
DB_PASSWORD=IHR-SICHERES-PASSWORT-HIER
DB_HOST=localhost
DB_PORT=5432

# ===========================
# SECURITY (HTTPS in Produktion)
# ===========================
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# ===========================
# CORS - Erlaubte Domains
# ===========================
# Fügen Sie ALLE Websites hinzu, die auf die API zugreifen dürfen
CORS_ALLOWED_ORIGINS=https://palmdynamicx.de,https://www.palmdynamicx.de,https://app.palmdynamicx.de
CSRF_TRUSTED_ORIGINS=https://auth.palmdynamicx.de,https://palmdynamicx.de,https://www.palmdynamicx.de,https://app.palmdynamicx.de

# ===========================
# JWT TOKENS
# ===========================
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=ihr-jwt-secret-key-separat-vom-django-secret

# ===========================
# EMAIL (SMTP)
# ===========================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@palmdynamicx.de
EMAIL_HOST_PASSWORD=ihr-email-passwort-oder-app-password
DEFAULT_FROM_EMAIL=PalmDynamicX Auth <noreply@palmdynamicx.de>

# ===========================
# FRONTEND URLs
# ===========================
FRONTEND_URL=https://palmdynamicx.de

# ===========================
# SOCIAL LOGIN (Optional)
# ===========================
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# ===========================
# REDIS (Optional - für Caching)
# ===========================
# REDIS_URL=redis://localhost:6379/0
```

### 4. Secret Key generieren

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Kopieren Sie den generierten Key in `.env` als `SECRET_KEY`.

### 5. Datenbank migrieren

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## 🌐 Nginx-Konfiguration

### Nginx-Config erstellen:

```bash
sudo nano /etc/nginx/sites-available/auth.palmdynamicx.de
```

**Inhalt:**

```nginx
# Rate Limiting Zones
limit_req_zone $binary_remote_addr zone=auth_login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=auth_api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth_register:10m rate=3r/m;

# HTTP zu HTTPS Redirect
server {
    listen 80;
    server_name auth.palmdynamicx.de www.auth.palmdynamicx.de;
    
    # Let's Encrypt Challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Alles andere zu HTTPS
    location / {
        return 301 https://auth.palmdynamicx.de$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name auth.palmdynamicx.de;
    
    # SSL-Zertifikate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/auth.palmdynamicx.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auth.palmdynamicx.de/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/auth.palmdynamicx.de/chain.pem;
    
    # SSL-Konfiguration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
    
    # CORS Headers (zusätzlich zu Django)
    add_header Access-Control-Allow-Origin $http_origin always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-CSRFToken" always;
    
    # Preflight-Requests
    if ($request_method = 'OPTIONS') {
        return 204;
    }
    
    # Logs
    access_log /var/log/nginx/auth.palmdynamicx.de.access.log;
    error_log /var/log/nginx/auth.palmdynamicx.de.error.log;
    
    # Max Upload Size
    client_max_body_size 10M;
    
    # Static Files
    location /static/ {
        alias /home/palmdynamicx/Auth-Service/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /home/palmdynamicx/Auth-Service/media/;
        expires 30d;
    }
    
    # Rate Limiting für Login
    location /api/accounts/login/ {
        limit_req zone=auth_login burst=3 nodelay;
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/proxy_params;
    }
    
    # Rate Limiting für Registrierung
    location /api/accounts/register/ {
        limit_req zone=auth_register burst=2 nodelay;
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/proxy_params;
    }
    
    # API Rate Limiting
    location /api/ {
        limit_req zone=auth_api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/proxy_params;
    }
    
    # Alle anderen Anfragen
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}

# www zu non-www Redirect
server {
    listen 443 ssl http2;
    server_name www.auth.palmdynamicx.de;
    
    ssl_certificate /etc/letsencrypt/live/auth.palmdynamicx.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auth.palmdynamicx.de/privkey.pem;
    
    return 301 https://auth.palmdynamicx.de$request_uri;
}
```

### Nginx aktivieren:

```bash
# Symlink erstellen
sudo ln -s /etc/nginx/sites-available/auth.palmdynamicx.de /etc/nginx/sites-enabled/

# Nginx-Konfiguration testen
sudo nginx -t

# Nginx neu starten
sudo systemctl restart nginx
```

---

## 🔄 Gunicorn mit Supervisor

### Gunicorn-Config erstellen:

```bash
nano /home/palmdynamicx/Auth-Service/gunicorn_config.py
```

**Inhalt:**

```python
import multiprocessing

# Server Socket
bind = '127.0.0.1:8000'
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/home/palmdynamicx/Auth-Service/logs/gunicorn_access.log'
errorlog = '/home/palmdynamicx/Auth-Service/logs/gunicorn_error.log'
loglevel = 'info'

# Process Naming
proc_name = 'auth_service'

# Server Mechanics
daemon = False
pidfile = '/home/palmdynamicx/Auth-Service/gunicorn.pid'
user = 'palmdynamicx'
group = 'palmdynamicx'
umask = 0o007

# SSL (falls direkt über Gunicorn)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'
```

### Logs-Verzeichnis erstellen:

```bash
mkdir -p /home/palmdynamicx/Auth-Service/logs
```

### Supervisor-Config erstellen:

```bash
sudo nano /etc/supervisor/conf.d/auth_service.conf
```

**Inhalt:**

```ini
[program:auth_service]
command=/home/palmdynamicx/Auth-Service/venv/bin/gunicorn auth_service.wsgi:application -c /home/palmdynamicx/Auth-Service/gunicorn_config.py
directory=/home/palmdynamicx/Auth-Service
user=palmdynamicx
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/palmdynamicx/Auth-Service/logs/supervisor.log
stderr_logfile=/home/palmdynamicx/Auth-Service/logs/supervisor_error.log
environment=PATH="/home/palmdynamicx/Auth-Service/venv/bin"
```

### Supervisor starten:

```bash
# Konfiguration neu laden
sudo supervisorctl reread
sudo supervisorctl update

# Service starten
sudo supervisorctl start auth_service

# Status prüfen
sudo supervisorctl status auth_service
```

---

## 🌍 CORS für andere Websites konfigurieren

### Neue Website hinzufügen:

1. **In `.env` Datei:**

```bash
# Neue Domain hinzufügen
CORS_ALLOWED_ORIGINS=https://palmdynamicx.de,https://app.palmdynamicx.de,https://shop.palmdynamicx.de
CSRF_TRUSTED_ORIGINS=https://auth.palmdynamicx.de,https://palmdynamicx.de,https://app.palmdynamicx.de,https://shop.palmdynamicx.de
```

2. **Django neustarten:**

```bash
sudo supervisorctl restart auth_service
```

3. **Website im Admin registrieren:**

Gehen Sie zu `https://auth.palmdynamicx.de/admin/` und erstellen Sie eine neue Website mit:
- **Name:** Shop Website
- **Domain:** shop.palmdynamicx.de
- **Callback URL:** https://shop.palmdynamicx.de/auth/callback
- **Allowed Origins:** ["https://shop.palmdynamicx.de"]

### API von anderer Website aufrufen:

```javascript
// Beispiel: Von https://shop.palmdynamicx.de
async function loginFromShop(email, password) {
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // KEIN Authorization-Header beim Login
    },
    credentials: 'include',  // Wichtig für Cookies
    body: JSON.stringify({
      username: email,
      password: password
    })
  });
  
  const data = await response.json();
  
  // Token speichern
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}

// Authentifizierte Anfrage
async function getProfile() {
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/profile/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    credentials: 'include'
  });
  
  return await response.json();
}
```

---

## 📖 API-Dokumentation aufrufen

### Swagger UI (Interaktiv):

```
https://auth.palmdynamicx.de/api/docs/
```

**Features:**
- ✅ Alle Endpoints mit Beschreibungen
- ✅ "Try it out" - Direkt testen
- ✅ JWT-Token-Authentifizierung
- ✅ Request/Response-Beispiele
- ✅ Modell-Schemas

### OpenAPI Schema (JSON):

```
https://auth.palmdynamicx.de/api/schema/
```

### Vollständige Dokumentation:

Siehe die Markdown-Dateien im Repository:
- `API_REFERENCE.md` - Detaillierte API-Referenz
- `SECURITY.md` - Sicherheits-Guide
- `WEBSITE_INTEGRATION.md` - Integration-Guide

---

## 📊 Monitoring & Wartung

### Logs überwachen:

```bash
# Nginx Logs
sudo tail -f /var/log/nginx/auth.palmdynamicx.de.access.log
sudo tail -f /var/log/nginx/auth.palmdynamicx.de.error.log

# Gunicorn Logs
tail -f /home/palmdynamicx/Auth-Service/logs/gunicorn_access.log
tail -f /home/palmdynamicx/Auth-Service/logs/gunicorn_error.log

# Supervisor Logs
tail -f /home/palmdynamicx/Auth-Service/logs/supervisor.log

# Django Logs (falls konfiguriert)
tail -f /home/palmdynamicx/Auth-Service/logs/django.log
```

### Regelmäßige Backups:

```bash
# Datenbank-Backup
sudo -u postgres pg_dump auth_service_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup-Script erstellen
nano /home/palmdynamicx/backup.sh
```

**backup.sh:**

```bash
#!/bin/bash
BACKUP_DIR="/home/palmdynamicx/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Datenbank-Backup
sudo -u postgres pg_dump auth_service_db > $BACKUP_DIR/db_$DATE.sql

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: db_$DATE.sql"
```

```bash
chmod +x /home/palmdynamicx/backup.sh

# Cronjob für tägliches Backup (2:00 AM)
crontab -e
# Fügen Sie hinzu:
0 2 * * * /home/palmdynamicx/backup.sh >> /home/palmdynamicx/backup.log 2>&1
```

### Updates deployen:

```bash
cd /home/palmdynamicx/Auth-Service
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart auth_service
```

### Monitoring mit Systemd:

```bash
# Service-Status prüfen
sudo supervisorctl status auth_service

# Neustarten
sudo supervisorctl restart auth_service

# Stoppen
sudo supervisorctl stop auth_service

# Starten
sudo supervisorctl start auth_service
```

---

## 🔍 Troubleshooting

### Problem: CORS-Fehler

**Symptom:** `Access-Control-Allow-Origin` Fehler im Browser

**Lösung:**
1. Domain in `.env` hinzufügen: `CORS_ALLOWED_ORIGINS`
2. Django neustarten: `sudo supervisorctl restart auth_service`
3. Browser-Cache leeren

### Problem: 502 Bad Gateway

**Symptom:** Nginx zeigt 502-Fehler

**Lösung:**
```bash
# Gunicorn-Status prüfen
sudo supervisorctl status auth_service

# Logs prüfen
tail -f /home/palmdynamicx/Auth-Service/logs/gunicorn_error.log

# Service neustarten
sudo supervisorctl restart auth_service
```

### Problem: SSL-Zertifikat abgelaufen

**Symptom:** Browser warnt vor ungültigem Zertifikat

**Lösung:**
```bash
# Zertifikat erneuern
sudo certbot renew

# Nginx neustarten
sudo systemctl restart nginx
```

### Problem: Datenbank-Verbindung fehlgeschlagen

**Symptom:** `OperationalError: connection refused`

**Lösung:**
```bash
# PostgreSQL-Status prüfen
sudo systemctl status postgresql

# PostgreSQL starten
sudo systemctl start postgresql

# Credentials in .env prüfen
nano /home/palmdynamicx/Auth-Service/.env
```

---

## ✅ Checkliste vor Go-Live

### Sicherheit:
- [ ] `DEBUG=False` in `.env`
- [ ] Starke `SECRET_KEY` generiert
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] SSL-Zertifikat aktiv
- [ ] Alle Security-Header aktiviert
- [ ] CORS nur für vertrauenswürdige Domains
- [ ] Rate Limiting konfiguriert
- [ ] Firewall konfiguriert (nur Ports 80, 443, 22 offen)

### Datenbank:
- [ ] PostgreSQL statt SQLite
- [ ] Starkes DB-Passwort
- [ ] Regelmäßige Backups eingerichtet
- [ ] Backups getestet

### Monitoring:
- [ ] Log-Rotation konfiguriert
- [ ] Monitoring-Tool eingerichtet (optional: Sentry, New Relic)
- [ ] E-Mail-Benachrichtigungen bei Fehlern
- [ ] Uptime-Monitoring (optional: UptimeRobot)

### Funktionalität:
- [ ] API-Dokumentation erreichbar: https://auth.palmdynamicx.de/api/docs/
- [ ] Admin-Interface erreichbar: https://auth.palmdynamicx.de/admin/
- [ ] Login funktioniert
- [ ] Registrierung funktioniert
- [ ] E-Mail-Versand funktioniert
- [ ] Token-Refresh funktioniert
- [ ] CORS von anderen Websites funktioniert

---

## 📞 Support

Bei Problemen:
- Logs prüfen (siehe Monitoring-Sektion)
- GitHub Issues: https://github.com/PalmDynamicX/Auth-Service/issues
- E-Mail: support@palmdynamicx.de

---

**Deployment erfolgreich! 🚀**

Ihre API ist jetzt verfügbar unter:
- **API-Dokumentation:** https://auth.palmdynamicx.de/api/docs/
- **Admin:** https://auth.palmdynamicx.de/admin/
- **API-Endpunkte:** https://auth.palmdynamicx.de/api/
