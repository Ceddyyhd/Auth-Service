"""
SMTP Email Debugging Guide
Lösung für: "Authentication Failed (535)" Fehler
"""

# 🔴 PROBLEM: Authentication Failed (535)

## Häufigste Ursachen:

### 1. Gmail/Google Workspace
❌ **Normale Passwörter funktionieren NICHT mehr!**

✅ **Lösung - App-Passwort verwenden:**

1. Gehe zu: https://myaccount.google.com/apppasswords
2. Erstelle ein neues App-Passwort für "Mail"
3. Verwende das 16-stellige App-Passwort (ohne Leerzeichen)

**Konfiguration für Gmail:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # App-Passwort (16 Zeichen)
DEFAULT_FROM_EMAIL=deine-email@gmail.com
```

**Oder Port 465 mit SSL:**
```bash
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

---

### 2. Microsoft 365 / Outlook.com

**Konfiguration:**
```bash
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=deine-email@outlook.com
EMAIL_HOST_PASSWORD=dein-passwort
```

**Alternative (Office365):**
```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
```

---

### 3. Allgemeiner SMTP (z.B. eigener Server)

```bash
EMAIL_HOST=mail.deine-domain.de
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=absender@deine-domain.de
EMAIL_HOST_PASSWORD=dein-passwort
```

---

## 🔧 Debug-Schritte:

### 1. Überprüfe Settings in Django Shell:

```bash
python manage.py shell
```

```python
from django.conf import settings

print("EMAIL_HOST:", settings.EMAIL_HOST)
print("EMAIL_PORT:", settings.EMAIL_PORT)
print("EMAIL_USE_TLS:", settings.EMAIL_USE_TLS)
print("EMAIL_USE_SSL:", settings.EMAIL_USE_SSL)
print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)
print("EMAIL_HOST_PASSWORD (gesetzt):", bool(settings.EMAIL_HOST_PASSWORD))
print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
```

### 2. Teste SMTP-Verbindung direkt:

```python
import smtplib
from django.conf import settings

try:
    # TLS Verbindung (Port 587)
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.set_debuglevel(1)  # Zeige Debug-Infos
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print("✅ SMTP Login erfolgreich!")
    server.quit()
except Exception as e:
    print(f"❌ Fehler: {e}")
```

### 3. Teste mit Django send_mail:

```python
from django.core.mail import send_mail

try:
    send_mail(
        'Test Subject',
        'Test Message',
        settings.DEFAULT_FROM_EMAIL,
        ['empfaenger@example.com'],
        fail_silently=False,
    )
    print("✅ E-Mail gesendet!")
except Exception as e:
    print(f"❌ Fehler: {e}")
```

---

## 🔍 Häufige Fehler und Lösungen:

### Fehler: "Authentication Failed"
- ✅ Bei Gmail: App-Passwort verwenden, nicht normales Passwort
- ✅ Bei Outlook: "Weniger sichere Apps" aktivieren oder modernen Auth verwenden
- ✅ Benutzername = vollständige E-Mail-Adresse
- ✅ Passwort ohne Leerzeichen eingeben

### Fehler: "Connection Timeout"
- ✅ Firewall-Regeln prüfen (Port 587/465 offen?)
- ✅ Server IP-Adresse ggf. bei Provider freischalten
- ✅ TLS/SSL Einstellungen prüfen

### Fehler: "SMTPServerDisconnected"
- ✅ EMAIL_USE_TLS und EMAIL_USE_SSL nicht gleichzeitig verwenden
- ✅ Port 587 = TLS, Port 465 = SSL

### Fehler: "Sender address rejected"
- ✅ DEFAULT_FROM_EMAIL muss mit EMAIL_HOST_USER übereinstimmen
- ✅ Domain muss bei Provider verifiziert sein

---

## 📝 Korrekte .env Konfiguration für Gmail:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=auth.palmdynamicx.de,www.auth.palmdynamicx.de

# Email Settings (GMAIL)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # 16-stelliges App-Passwort ohne Leerzeichen!
DEFAULT_FROM_EMAIL=deine-email@gmail.com
SERVER_EMAIL=deine-email@gmail.com

# Email URLs (für Links in E-Mails)
EMAIL_VERIFY_URL=https://deine-website.com/verify-email
PASSWORD_RESET_URL=https://deine-website.com/reset-password

# Token Expiry
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRY_HOURS=1
```

---

## 🧪 Test-Endpoint verwenden:

```bash
# GET: Aktuelle Konfiguration anzeigen
curl -X GET https://auth.palmdynamicx.de/api/accounts/smtp-config/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# POST: Test-E-Mail senden
curl -X POST https://auth.palmdynamicx.de/api/accounts/test-smtp/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_email": "test@example.com"}'
```

---

## 🔐 Gmail App-Passwort erstellen:

1. Gehe zu: https://myaccount.google.com/security
2. Aktiviere "2-Faktor-Authentifizierung" (falls noch nicht aktiv)
3. Gehe zu: https://myaccount.google.com/apppasswords
4. Wähle "Mail" und "Anderes Gerät"
5. Name: "Django Auth Service"
6. Klicke "Erstellen"
7. Kopiere das 16-stellige Passwort (z.B. "abcd efgh ijkl mnop")
8. Verwende es in .env OHNE Leerzeichen: `abcdefghijklmnop`

---

## ⚠️ Wichtig für Production:

```bash
# Niemals in settings.py hart-codieren!
# Immer über Umgebungsvariablen:

# Linux/Mac:
export EMAIL_HOST_PASSWORD="your-app-password"

# Windows:
$env:EMAIL_HOST_PASSWORD="your-app-password"

# Docker:
# In docker-compose.yml oder .env file
EMAIL_HOST_PASSWORD=your-app-password

# Systemd Service:
# In /etc/systemd/system/authservice.service
Environment="EMAIL_HOST_PASSWORD=your-app-password"
```

---

## 📊 Logs überprüfen:

```bash
# Django Logs
tail -f /var/log/gunicorn/error.log

# Systemd Service Logs
journalctl -u authservice -f

# Im Code: Aktiviere SMTP Debug
# In Django settings.py temporär:
EMAIL_DEBUG = True
```

---

## 🚀 Nach Konfigurationsänderung:

```bash
# Service neu starten
sudo systemctl restart authservice

# Oder mit gunicorn
sudo systemctl restart gunicorn

# Docker
docker-compose restart

# Logs prüfen
journalctl -u authservice -n 50
```

---

**Tipp:** Verwende den neuen SMTP-Debug-Endpoint (siehe unten) für detaillierte Fehleranalyse!
