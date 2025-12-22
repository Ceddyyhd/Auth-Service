#!/bin/bash

###############################################################################
# Auth-Service Deployment Script für Debian 12
# Domain: auth.palmdynamicx.de
# 
# Dieses Script:
# - Installiert alle Dependencies (Python, PostgreSQL, Redis, NGINX)
# - Richtet die Datenbank ein
# - Konfiguriert Gunicorn als WSGI-Server
# - Konfiguriert NGINX als Reverse Proxy
# - Richtet SSL mit Let's Encrypt ein
# - Erstellt Systemd Services für Auto-Start
###############################################################################

set -e  # Exit bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Konfiguration
DOMAIN="auth.palmdynamicx.de"
APP_DIR="/var/www/auth-service"
APP_USER="authservice"
PYTHON_VERSION="3.11"
DB_NAME="auth_service_db"
DB_USER="auth_service_user"
DB_PASSWORD=$(openssl rand -base64 32)
GITHUB_REPO="https://github.com/Ceddyyhd/Auth-Service.git"
GITHUB_BRANCH="main"
# GitHub Personal Access Token (WICHTIG: Diese Datei nicht public sharen!)
GITHUB_TOKEN="XXXX"

echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Auth-Service Deployment für Debian 12           ║${NC}"
echo -e "${GREEN}║   Domain: $DOMAIN                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Root-Check
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Bitte als root ausführen (sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/10] System-Update...${NC}"
apt update
apt upgrade -y

echo -e "${YELLOW}[2/10] Installiere Dependencies...${NC}"
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    curl \
    certbot \
    python3-certbot-nginx \
    build-essential \
    libpq-dev \
    python3.11-dev

echo -e "${YELLOW}[3/10] Erstelle Benutzer '$APP_USER'...${NC}"
if id "$APP_USER" &>/dev/null; then
    echo "Benutzer existiert bereits"
else
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✓ Benutzer erstellt${NC}"
fi

echo -e "${YELLOW}[4/10] Erstelle App-Verzeichnis...${NC}"
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

echo -e "${YELLOW}[5/10] PostgreSQL-Datenbank einrichten...${NC}"
sudo -u postgres psql <<EOF
-- Lösche existierende Datenbank falls vorhanden
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Erstelle neuen User und Datenbank
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Erweiterte Rechte für Django
ALTER USER $DB_USER CREATEDB;
EOF

echo -e "${GREEN}✓ Datenbank '$DB_NAME' erstellt${NC}"
echo -e "${GREEN}✓ User: $DB_USER${NC}"
echo -e "${GREEN}✓ Password: $DB_PASSWORD${NC}"

# Speichere DB-Credentials für später
echo "DB_NAME=$DB_NAME" > /root/.auth_service_db_creds
echo "DB_USER=$DB_USER" >> /root/.auth_service_db_creds
echo "DB_PASSWORD=$DB_PASSWORD" >> /root/.auth_service_db_creds
chmod 600 /root/.auth_service_db_creds

echo -e "${YELLOW}[6/10] Redis konfigurieren...${NC}"
systemctl enable redis-server
systemctl start redis-server
echo -e "${GREEN}✓ Redis läuft${NC}"

echo -e "${YELLOW}[7/10] Code von GitHub klonen...${NC}"
echo ""
echo -e "${GREEN}Repository: $GITHUB_REPO${NC}"
echo -e "${GREEN}Branch: $GITHUB_BRANCH${NC}"
echo ""

# Prüfe ob Verzeichnis existiert
if [ -d "$APP_DIR/.git" ]; then
    echo -e "${YELLOW}Repository existiert bereits. Pull wird durchgeführt...${NC}"
    cd $APP_DIR
    sudo -u $APP_USER git pull https://${GITHUB_TOKEN}@github.com/Ceddyyhd/Auth-Service.git $GITHUB_BRANCH
else
    echo -e "${YELLOW}Klone Repository...${NC}"
    # Clone mit Token
    sudo -u $APP_USER git clone --branch $GITHUB_BRANCH https://${GITHUB_TOKEN}@github.com/Ceddyyhd/Auth-Service.git $APP_DIR
    
    # Entferne Token aus Git-Config für Sicherheit
    cd $APP_DIR
    sudo -u $APP_USER git remote set-url origin $GITHUB_REPO
fi

# Token für spätere Updates speichern
echo "GITHUB_TOKEN=$GITHUB_TOKEN" > /root/.auth_service_github_token
chmod 600 /root/.auth_service_github_token

echo -e "${GREEN}✓ Code von GitHub heruntergeladen${NC}"
echo -e "${GREEN}✓ Token gespeichert für zukünftige Updates${NC}"

# Wechsle zum App-User für den Rest
echo -e "${YELLOW}[8/10] Python Virtual Environment einrichten...${NC}"
sudo -u $APP_USER bash <<EOSU
cd $APP_DIR

# Virtual Environment erstellen
python3.11 -m venv venv
source venv/bin/activate

# Pip upgraden
pip install --upgrade pip

# Dependencies installieren
pip install -r requirements.txt

# Gunicorn installieren
pip install gunicorn

echo -e "${GREEN}✓ Python-Dependencies installiert${NC}"
EOSU

echo -e "${YELLOW}[9/10] Django-Projekt konfigurieren...${NC}"

# Generiere Django SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
JWT_SECRET=$(openssl rand -base64 64)

# Erstelle .env Datei
cat > $APP_DIR/.env <<EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=$JWT_SECRET
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Email (später konfigurieren)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@$DOMAIN
SERVER_EMAIL=server@$DOMAIN

# Frontend URL (anpassen an deine Frontend-Domains)
FRONTEND_URL=https://$DOMAIN

# SSO Settings
SESSION_COOKIE_DOMAIN=.$DOMAIN
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

echo -e "${GREEN}✓ .env Datei erstellt${NC}"

# Django Setup
sudo -u $APP_USER bash <<EOSU
cd $APP_DIR
source venv/bin/activate

# Migrationen
python manage.py migrate

# Static Files sammeln
python manage.py collectstatic --noinput

# Superuser erstellen (interaktiv)
echo ""
echo -e "${YELLOW}Erstelle Django Superuser:${NC}"
python manage.py createsuperuser

echo -e "${GREEN}✓ Django konfiguriert${NC}"
EOSU

echo -e "${YELLOW}[10/10] Systemd Services & NGINX konfigurieren...${NC}"

# Erstelle Gunicorn Socket
cat > /etc/systemd/system/authservice.socket <<EOF
[Unit]
Description=Auth Service Gunicorn Socket

[Socket]
ListenStream=/run/authservice.sock

[Install]
WantedBy=sockets.target
EOF

# Erstelle Gunicorn Service
cat > /etc/systemd/system/authservice.service <<EOF
[Unit]
Description=Auth Service Gunicorn Daemon
Requires=authservice.socket
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn \\
          --workers 4 \\
          --threads 2 \\
          --worker-class gthread \\
          --bind unix:/run/authservice.sock \\
          --access-logfile /var/log/authservice/access.log \\
          --error-logfile /var/log/authservice/error.log \\
          --log-level info \\
          auth_service.wsgi:application

ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Log-Verzeichnis erstellen
mkdir -p /var/log/authservice
chown $APP_USER:$APP_USER /var/log/authservice

# NGINX-Konfiguration (ohne SSL zuerst)
cat > /etc/nginx/sites-available/authservice <<EOF
# HTTP - Redirect zu HTTPS (wird nach Certbot-Setup automatisch)
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    # Für Let's Encrypt Challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Temporär für Certbot - später wird das zu HTTPS-Redirect
    location / {
        proxy_pass http://unix:/run/authservice.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Aktiviere Site
ln -sf /etc/nginx/sites-available/authservice /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Teste NGINX Config
nginx -t

# Starte Services
systemctl daemon-reload
systemctl enable authservice.socket
systemctl enable authservice.service
systemctl start authservice.socket
systemctl start authservice.service
systemctl enable nginx
systemctl restart nginx

echo -e "${GREEN}✓ Services gestartet${NC}"

# Status Check
echo ""
echo -e "${YELLOW}Service Status:${NC}"
systemctl status authservice.service --no-pager | head -n 10
systemctl status nginx --no-pager | head -n 5

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}║             Deployment Fast Fertig!             ║${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Nächste Schritte:${NC}"
echo ""
echo "1. DNS-Eintrag prüfen:"
echo "   Stelle sicher, dass $DOMAIN auf diese Server-IP zeigt"
echo ""
echo "2. SSL-Zertifikat installieren:"
echo "   ${GREEN}certbot --nginx -d $DOMAIN -d www.$DOMAIN${NC}"
echo ""
echo "3. Firewall konfigurieren:"
echo "   ${GREEN}ufw allow 'Nginx Full'${NC}"
echo "   ${GREEN}ufw allow OpenSSH${NC}"
echo "   ${GREEN}ufw enable${NC}"
echo ""
echo "4. Test durchführen:"
echo "   ${GREEN}curl http://$DOMAIN/api/schema/${NC}"
echo ""
echo "5. Admin-Panel besuchen:"
echo "   https://$DOMAIN/admin/"
echo ""
echo -e "${YELLOW}Wichtige Dateien:${NC}"
echo "  • App-Verzeichnis: $APP_DIR"
echo "  • .env Datei: $APP_DIR/.env"
echo "  • NGINX Config: /etc/nginx/sites-available/authservice"
echo "  • Systemd Service: /etc/systemd/system/authservice.service"
echo "  • Logs: /var/log/authservice/"
echo "  • DB Credentials: /root/.auth_service_db_creds"
echo ""
echo -e "${YELLOW}Nützliche Befehle:${NC}"
echo "  • Service neustarten: ${GREEN}systemctl restart authservice${NC}"
echo "  • Logs ansehen: ${GREEN}journalctl -u authservice -f${NC}"
echo "  • NGINX neustarten: ${GREEN}systemctl restart nginx${NC}"
echo "  • NGINX Logs: ${GREEN}tail -f /var/log/nginx/error.log${NC}"
echo ""
echo -e "${GREEN}✓ Deployment abgeschlossen!${NC}"
