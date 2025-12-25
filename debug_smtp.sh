#!/bin/bash
# SMTP Debug Script für Production Server
# Führe dieses Script auf deinem Server aus, um E-Mail-Probleme zu diagnostizieren

echo "🔍 SMTP Konfiguration überprüfen..."
echo "=================================="
echo ""

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Prüfe Umgebungsvariablen
echo "📋 1. Umgebungsvariablen prüfen:"
echo "================================"

if [ -f "/var/www/auth-service/.env" ]; then
    echo -e "${GREEN}✅ .env Datei gefunden${NC}"
    
    # Zeige E-Mail-Konfiguration (ohne Passwörter)
    echo ""
    echo "E-Mail Konfiguration (.env):"
    grep -E "^EMAIL_|^DEFAULT_FROM_EMAIL|^SERVER_EMAIL" /var/www/auth-service/.env | sed 's/=.*PASSWORD.*/=***HIDDEN***/'
else
    echo -e "${RED}❌ .env Datei nicht gefunden in /var/www/auth-service/${NC}"
fi

echo ""
echo "================================"
echo ""

# 2. Django Settings überprüfen
echo "⚙️ 2. Django Settings überprüfen:"
echo "================================"

cd /var/www/auth-service

# Aktiviere Virtual Environment falls vorhanden
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Django Shell Commands
python3 manage.py shell << 'PYTHON_EOF'
from django.conf import settings
print("\n📧 E-Mail Konfiguration in Django:")
print("=" * 50)
print(f"Backend:      {settings.EMAIL_BACKEND}")
print(f"Host:         {settings.EMAIL_HOST}")
print(f"Port:         {settings.EMAIL_PORT}")
print(f"Use TLS:      {settings.EMAIL_USE_TLS}")
print(f"Use SSL:      {getattr(settings, 'EMAIL_USE_SSL', False)}")
print(f"Host User:    {settings.EMAIL_HOST_USER}")
print(f"Password Set: {'✅ Ja' if settings.EMAIL_HOST_PASSWORD else '❌ Nein'}")
print(f"From Email:   {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)
PYTHON_EOF

echo ""
echo "================================"
echo ""

# 3. SMTP Verbindungstest
echo "🔌 3. SMTP Verbindung testen:"
echo "================================"

python3 manage.py shell << 'PYTHON_EOF'
import smtplib
from django.conf import settings

print("\n🧪 Teste SMTP Verbindung...")

try:
    # DNS Resolution
    import socket
    socket.gethostbyname(settings.EMAIL_HOST)
    print(f"✅ DNS: {settings.EMAIL_HOST} ist erreichbar")
    
    # Verbindung aufbauen
    if getattr(settings, 'EMAIL_USE_SSL', False):
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        print(f"✅ SSL Verbindung zu {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    else:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        print(f"✅ SMTP Verbindung zu {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        if settings.EMAIL_USE_TLS:
            server.starttls()
            print("✅ TLS STARTTLS erfolgreich")
    
    # Authentifizierung
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print(f"✅ Authentifizierung erfolgreich für: {settings.EMAIL_HOST_USER}")
    
    server.quit()
    print("\n🎉 ALLE TESTS ERFOLGREICH!")
    print("\n💡 SMTP ist korrekt konfiguriert und funktioniert.")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTIFIZIERUNGSFEHLER: {e}")
    print("\n🔧 LÖSUNGSVORSCHLÄGE:")
    
    if 'gmail' in settings.EMAIL_HOST.lower():
        print("   📱 GMAIL LÖSUNG:")
        print("   1. Gehe zu: https://myaccount.google.com/apppasswords")
        print("   2. Erstelle ein App-Passwort für 'Mail'")
        print("   3. Verwende das 16-stellige Passwort (ohne Leerzeichen)")
        print("   4. Aktualisiere EMAIL_HOST_PASSWORD in .env")
        print("   5. Service neu starten: sudo systemctl restart authservice")
    elif 'outlook' in settings.EMAIL_HOST.lower():
        print("   📧 OUTLOOK LÖSUNG:")
        print("   1. Aktiviere SMTP AUTH in deinem Outlook-Account")
        print("   2. Verwende moderne Authentifizierung")
        print("   3. Prüfe, ob das Passwort korrekt ist")
    else:
        print("   📮 ALLGEMEINE LÖSUNG:")
        print("   1. Prüfe Benutzername (meist die vollständige E-Mail)")
        print("   2. Prüfe Passwort (keine Leerzeichen!)")
        print("   3. Prüfe bei deinem Provider, ob SMTP aktiviert ist")
        
except socket.gaierror as e:
    print(f"\n❌ DNS FEHLER: Hostname konnte nicht aufgelöst werden")
    print(f"   {e}")
    print("\n🔧 Prüfe EMAIL_HOST in der .env Datei")
    
except socket.timeout:
    print(f"\n❌ TIMEOUT: Server antwortet nicht")
    print("\n🔧 LÖSUNGSVORSCHLÄGE:")
    print("   1. Prüfe Firewall-Regeln (Port muss offen sein)")
    print("   2. Prüfe ob der Host korrekt ist")
    print("   3. Teste mit: telnet {settings.EMAIL_HOST} {settings.EMAIL_PORT}")
    
except Exception as e:
    print(f"\n❌ FEHLER: {type(e).__name__}: {e}")

PYTHON_EOF

echo ""
echo "================================"
echo ""

# 4. Zeige Service Status
echo "🔄 4. Service Status:"
echo "================================"
systemctl status authservice --no-pager | head -n 20

echo ""
echo "================================"
echo ""

# 5. Zeige letzte Logs
echo "📋 5. Letzte Service Logs:"
echo "================================"
journalctl -u authservice -n 30 --no-pager

echo ""
echo "================================"
echo ""
echo "✅ Debug-Script abgeschlossen!"
echo ""
echo "📚 Weitere Hilfe:"
echo "   - Siehe EMAIL_TROUBLESHOOTING.md"
echo "   - API Endpoint: POST /api/accounts/test-smtp/"
echo "   - Service neu starten: sudo systemctl restart authservice"
echo ""
