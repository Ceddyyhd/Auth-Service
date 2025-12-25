# 🔧 Zoho SMTP Authentifizierungsfehler - Lösung

## 🔴 Problem identifiziert:

```bash
EMAIL_HOST_USER=c.schwieger@palmstudios.de       # Authentifizierung
DEFAULT_FROM_EMAIL=palmservers@palmstudios.de    # Absender (anders!)
```

**Fehler:** `(535, b'Authentication Failed')`

## ✅ Lösungen:

### **Option 1: Absender-Adresse anpassen (SCHNELLSTE LÖSUNG)**

Ändere in `/var/www/auth-service/.env`:

```bash
# Verwende die gleiche E-Mail für Login und Absender
DEFAULT_FROM_EMAIL=c.schwieger@palmstudios.de
SERVER_EMAIL=c.schwieger@palmstudios.de
```

Dann Service neu starten:
```bash
sudo systemctl restart authservice
```

---

### **Option 2: Alias in Zoho konfigurieren (EMPFOHLEN)**

Wenn du wirklich von `palmservers@palmstudios.de` senden möchtest:

1. **In Zoho Mail einloggen** mit `c.schwieger@palmstudios.de`
2. Gehe zu **Settings** → **Email Addresses**
3. Klicke **Add Email Address**
4. Füge `palmservers@palmstudios.de` als **Alias** hinzu
5. Verifiziere den Alias (Zoho sendet eine Bestätigungs-E-Mail)
6. Nach Verifizierung funktioniert das Senden als `palmservers@palmstudios.de`

**Keine Änderung an .env nötig nach diesem Schritt!**

---

### **Option 3: Separaten Account verwenden**

Erstelle ein separates Zoho-Konto für `palmservers@palmstudios.de`:

```bash
EMAIL_HOST_USER=palmservers@palmstudios.de
EMAIL_HOST_PASSWORD=neues-passwort-hier
DEFAULT_FROM_EMAIL=palmservers@palmstudios.de
SERVER_EMAIL=palmservers@palmstudios.de
```

---

## 🔧 Zoho-spezifische SMTP-Konfiguration

### Korrekte Zoho SMTP Settings:

**Für smtppro.zoho.eu (Europa):**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtppro.zoho.eu
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=deine-email@palmstudios.de
EMAIL_HOST_PASSWORD=dein-passwort
DEFAULT_FROM_EMAIL=deine-email@palmstudios.de  # MUSS GLEICH SEIN!
SERVER_EMAIL=deine-email@palmstudios.de
```

**Alternative Ports:**
- Port 587 mit TLS (empfohlen) ✅
- Port 465 mit SSL:
  ```bash
  EMAIL_PORT=465
  EMAIL_USE_TLS=False
  EMAIL_USE_SSL=True
  ```

---

## ⚠️ Wichtige Zoho-Regeln:

1. **Absender muss authentifizierter Benutzer oder Alias sein**
   - ❌ Login: user1@domain.com, Send: user2@domain.com → FEHLER
   - ✅ Login: user1@domain.com, Send: user1@domain.com → OK
   - ✅ Login: user1@domain.com, Send: alias@domain.com (wenn konfiguriert) → OK

2. **App-Passwörter verwenden (bei 2FA)**
   - Falls 2-Faktor-Authentifizierung aktiv ist
   - Erstelle App-Passwort in Zoho

3. **SMTP muss in Zoho aktiviert sein**
   - Settings → Mail → SMTP Settings
   - "Allow SMTP" muss aktiviert sein

4. **Rate Limits beachten**
   - Zoho Free: 250 E-Mails/Tag
   - Zoho Mail Premium: 50.000 E-Mails/Tag
   - Pro Account: 100.000 E-Mails/Tag

---

## 🧪 Nach der Änderung testen:

```bash
# 1. Service neu starten
sudo systemctl restart authservice

# 2. Debug-Script erneut ausführen
cd /var/www/auth-service
./debug_smtp.sh

# Oder über API:
curl -X POST https://auth.palmdynamicx.de/api/accounts/test-smtp/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_email":"test@example.com"}'
```

---

## 📋 Vollständige .env Beispielkonfiguration:

```bash
# Django
DEBUG=False
SECRET_KEY=dein-geheimer-schluessel
ALLOWED_HOSTS=auth.palmdynamicx.de,www.auth.palmdynamicx.de

# Datenbank
DATABASE_URL=mysql://user:password@localhost:3306/auth_db

# Email (Zoho SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtppro.zoho.eu
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=c.schwieger@palmstudios.de
EMAIL_HOST_PASSWORD=Adq5U@RzN9cGigU
DEFAULT_FROM_EMAIL=c.schwieger@palmstudios.de  # ← HIER GEÄNDERT!
SERVER_EMAIL=c.schwieger@palmstudios.de        # ← HIER GEÄNDERT!

# Email URLs
EMAIL_VERIFY_URL=https://deine-website.com/verify-email
PASSWORD_RESET_URL=https://deine-website.com/reset-password

# Token Expiry
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRY_HOURS=1

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🔍 Erweiterte Zoho-Fehlersuche:

### 1. Test mit Python direkt:

```python
import smtplib
from email.mime.text import MIMEText

smtp_user = "c.schwieger@palmstudios.de"
smtp_pass = "Adq5U@RzN9cGigU"
from_email = "c.schwieger@palmstudios.de"  # GLEICH wie smtp_user!
to_email = "test@example.com"

msg = MIMEText("Test von Zoho")
msg['Subject'] = "Test"
msg['From'] = from_email
msg['To'] = to_email

server = smtplib.SMTP('smtppro.zoho.eu', 587)
server.starttls()
server.login(smtp_user, smtp_pass)
server.send_message(msg)
server.quit()
print("✅ Erfolgreich gesendet!")
```

### 2. Prüfe Zoho-Account-Status:

1. Login auf https://mail.zoho.eu
2. Gehe zu **Settings** → **Mail Accounts**
3. Prüfe **SMTP Status**: Muss "Enabled" sein
4. Prüfe **Sending Limits**: Nicht überschritten?
5. Prüfe **Allowed Senders**: Falls konfiguriert

### 3. Zoho Admin Console (falls vorhanden):

- https://mailadmin.zoho.eu
- **Email Sending** → **SMTP Settings**
- Stelle sicher, dass SMTP für die Domain aktiviert ist

---

## 🎯 QUICK FIX (jetzt sofort):

```bash
# Auf deinem Server:
cd /var/www/auth-service

# .env bearbeiten
nano .env

# Ändere diese Zeilen:
DEFAULT_FROM_EMAIL=c.schwieger@palmstudios.de
SERVER_EMAIL=c.schwieger@palmstudios.de

# Speichern: CTRL+X, dann Y, dann Enter

# Service neu starten
sudo systemctl restart authservice

# Testen
./debug_smtp.sh
```

**Das sollte sofort funktionieren!** ✅

---

## 📞 Wenn es immer noch nicht funktioniert:

1. **Prüfe Passwort:**
   ```bash
   # Stelle sicher, keine Leerzeichen am Ende:
   echo "EMAIL_HOST_PASSWORD=$(cat .env | grep EMAIL_HOST_PASSWORD | cut -d'=' -f2)"
   ```

2. **Prüfe SMTP-Zugriff in Zoho:**
   - https://mail.zoho.eu → Settings → SMTP
   - "Allow access to less secure apps" aktivieren (falls vorhanden)

3. **Kontaktiere Zoho Support:**
   - Manchmal blockiert Zoho neue Server-IPs
   - Bitte um Freischaltung deiner Server-IP

---

**Nach der Änderung sollte es sofort funktionieren!** 🚀
