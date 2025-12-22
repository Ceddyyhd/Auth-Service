#!/bin/bash

###############################################################################
# Quick Update Script für Auth-Service
# Führt Code-Updates durch ohne komplettes Re-Deployment
###############################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/var/www/auth-service"
APP_USER="authservice"

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Auth-Service Update Script              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Root-Check
if [ "$EUID" -ne 0 ]; then 
    echo "Bitte als root ausführen (sudo)"
    exit 1
fi

echo -e "${YELLOW}[1/7] Code-Update wird vorbereitet...${NC}"
cd $APP_DIR

echo -e "${YELLOW}[2/7] Git Pull / Code Sync...${NC}"
# Wenn Git verwendet wird:
if [ -d ".git" ]; then
    sudo -u $APP_USER git pull
else
    echo "Kein Git-Repository. Code manuell syncen mit:"
    echo "  rsync -avz --exclude='venv' ./ root@server:$APP_DIR/"
    echo ""
    read -p "Code bereits aktualisiert? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW}[3/7] Python Dependencies aktualisieren...${NC}"
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

echo -e "${YELLOW}[4/7] Django Migrationen...${NC}"
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
source venv/bin/activate
python manage.py migrate --noinput
EOF

echo -e "${YELLOW}[5/7] Static Files sammeln...${NC}"
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
source venv/bin/activate
python manage.py collectstatic --noinput --clear
EOF

echo -e "${YELLOW}[6/7] Service neustarten...${NC}"
systemctl restart authservice
sleep 2

echo -e "${YELLOW}[7/7] Status prüfen...${NC}"
if systemctl is-active --quiet authservice; then
    echo -e "${GREEN}✓ Service läuft${NC}"
    systemctl status authservice --no-pager | head -n 10
else
    echo -e "${RED}✗ Service-Fehler!${NC}"
    journalctl -u authservice -n 50 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Update abgeschlossen!${NC}"
echo ""
echo "Logs ansehen: journalctl -u authservice -f"
echo "Service Status: systemctl status authservice"
