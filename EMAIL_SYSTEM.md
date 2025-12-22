# 📧 Email-System Dokumentation

## Übersicht

Das Auth-Service System verfügt über ein vollständiges Email-System mit:
- ✅ **Email-Verifikation** - Bestätigung der Email-Adresse nach Registrierung
- 🔐 **Passwort-Reset** - Sicheres Zurücksetzen vergessener Passwörter  
- ⚙️ **SMTP-Konfiguration** - Flexible Email-Server Einstellungen
- 🧪 **Test-Funktion** - SMTP-Konfiguration testen

---

## 🔧 SMTP Konfiguration

### Umgebungsvariablen (.env)

```env
# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP Server Einstellungen
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Email Credentials
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Absender
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com

# Frontend URLs (für Email-Links)
FRONTEND_URL=http://localhost:3000
```

### Beliebte SMTP-Anbieter

#### Gmail
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
```

**Wichtig:** Für Gmail benötigst du ein [App-spezifisches Passwort](https://support.google.com/accounts/answer/185833)

#### Outlook/Office365
```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

#### SendGrid
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```env
EMAIL_HOST=email-smtp.eu-central-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
```

### Test-Modus (Entwicklung)

Für Entwicklung kannst du Console-Backend verwenden (Emails werden im Terminal angezeigt):

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 📬 API Endpoints

### 1. SMTP Konfiguration testen

**Test-Email senden:**

```http
POST /api/accounts/test-smtp/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "recipient_email": "test@example.com"
}
```

**Response (Erfolg):**
```json
{
  "message": "Test-E-Mail erfolgreich an test@example.com gesendet.",
  "smtp_config": {
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "use_ssl": false,
    "from_email": "your-email@gmail.com"
  }
}
```

**Response (Fehler):**
```json
{
  "error": "Fehler beim Senden der Test-E-Mail: [Detailed error message]",
  "smtp_config": {
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "use_ssl": false,
    "from_email": "your-email@gmail.com"
  }
}
```

⚠️ **Berechtigung:** Nur für Admins zugänglich

---

### 2. SMTP Konfiguration abrufen

```http
GET /api/accounts/smtp-config/
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "email_backend": "django.core.mail.backends.smtp.EmailBackend",
  "host": "smtp.gmail.com",
  "port": 587,
  "use_tls": true,
  "use_ssl": false,
  "from_email": "your-email@gmail.com",
  "host_user": "your-email@gmail.com",
  "host_password_configured": true,
  "verification_token_expiry_hours": 24,
  "password_reset_token_expiry_hours": 1
}
```

---

### 3. Email-Verifikation

#### Schritt 1: Registrierung (Email wird automatisch gesendet)

```http
POST /api/accounts/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "username": "newuser",
  "website_id": "website-uuid",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "is_verified": false
  },
  "tokens": {
    "access": "...",
    "refresh": "..."
  },
  "message": "Benutzer erfolgreich registriert.",
  "verification_email_sent": true
}
```

#### Schritt 2: Verifikations-Email erneut senden

```http
POST /api/accounts/resend-verification/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Bestätigungs-E-Mail wurde gesendet."
}
```

#### Schritt 3: Email bestätigen

```http
POST /api/accounts/verify-email/
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

**Response:**
```json
{
  "message": "E-Mail erfolgreich verifiziert.",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "is_verified": true
  }
}
```

---

### 4. Passwort Zurücksetzen

#### Schritt 1: Passwort-Reset anfordern

```http
POST /api/accounts/request-password-reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Passwort-Reset-E-Mail wurde gesendet."
}
```

#### Schritt 2: Neues Passwort setzen

```http
POST /api/accounts/reset-password/
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePass123!",
  "new_password2": "NewSecurePass123!"
}
```

**Response:**
```json
{
  "message": "Passwort erfolgreich zurückgesetzt."
}
```

⚠️ Nach erfolgreichem Reset erhält der Benutzer eine Benachrichtigungs-Email

---

## 🎨 Email-Templates

Alle Emails werden als HTML mit schönem Design versendet:

### Verifikations-Email
- **Betreff:** "Bestätige deine E-Mail-Adresse"
- **Farbe:** Grün (#4CAF50)
- **Gültigkeit:** 24 Stunden
- **Inhalt:** Willkommensnachricht + Bestätigungs-Button

### Passwort-Reset Email
- **Betreff:** "Passwort zurücksetzen"
- **Farbe:** Orange (#FF5722)
- **Gültigkeit:** 1 Stunde
- **Inhalt:** Reset-Button + Sicherheitshinweise

### Test-Email
- **Betreff:** "Test E-Mail - SMTP Konfiguration"
- **Farbe:** Blau (#2196F3)
- **Inhalt:** Erfolgsbestätigung + SMTP-Details

### Passwort-Änderung Benachrichtigung
- **Betreff:** "Dein Passwort wurde geändert"
- **Farbe:** Grün (#4CAF50)
- **Inhalt:** Sicherheitshinweis

---

## 🔐 Sicherheit

### Token-Verwaltung

```python
# Email Verification Token
- Gültigkeit: 24 Stunden (konfigurierbar)
- Einmalige Verwendung
- Kryptographisch sicher (secrets.token_urlsafe)
- Automatisch ungültig nach Verwendung

# Password Reset Token
- Gültigkeit: 1 Stunde (konfigurierbar)
- Einmalige Verwendung
- Kryptographisch sicher
- Automatisch ungültig nach Verwendung
```

### Best Practices

1. **Keine Benutzer-Preisgabe:** API gibt nie preis, ob eine Email existiert
2. **Rate Limiting:** Implementiere Rate Limiting für Email-Endpoints
3. **HTTPS:** Verwende immer HTTPS in Produktion
4. **App-Passwörter:** Bei Gmail immer App-spezifische Passwörter verwenden
5. **Token-Ablauf:** Tokens automatisch ungültig nach Ablaufzeit

---

## 📊 Admin Interface

### Email Verification Tokens

Im Admin-Panel unter **Accounts → Email Verification Tokens**:

Anzeige:
- Benutzer
- Token (gekürzt für Sicherheit)
- Erstellungszeit
- Ablaufzeit
- Status (verwendet/ungültig)
- Gültigkeit (Ja/Nein)

### Password Reset Tokens

Im Admin-Panel unter **Accounts → Password Reset Tokens**:

Anzeige:
- Benutzer
- Token (gekürzt)
- Erstellungszeit
- Ablaufzeit
- Status
- Gültigkeit

---

## 🛠️ Fehlerbehandlung

### Häufige Fehler

**1. SMTP Authentication Failed**
```
SMTPAuthenticationError: (535, 'Authentication failed')
```
**Lösung:** Überprüfe EMAIL_HOST_USER und EMAIL_HOST_PASSWORD

**2. Connection Refused**
```
ConnectionRefusedError: [Errno 111] Connection refused
```
**Lösung:** Überprüfe EMAIL_HOST und EMAIL_PORT

**3. TLS/SSL Fehler**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```
**Lösung:** Setze EMAIL_USE_TLS=True oder EMAIL_USE_SSL korrekt

**4. Timeout**
```
socket.timeout: timed out
```
**Lösung:** Firewall-Regeln prüfen, Port 587/465 erlauben

---

## 🧪 Testing

### Console Backend (Entwicklung)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails werden im Terminal ausgegeben statt versendet.

### Test mit echtem SMTP

```python
# Python Shell
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test Message',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Postman Collection

Füge diese Requests zur Postman Collection hinzu:

```json
{
  "name": "SMTP Test",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{access_token}}"
      },
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"recipient_email\": \"test@example.com\"\n}"
    },
    "url": {
      "raw": "{{base_url}}/api/accounts/test-smtp/",
      "host": ["{{base_url}}"],
      "path": ["api", "accounts", "test-smtp", ""]
    }
  }
}
```

---

## 🚀 Production Setup

### 1. Umgebungsvariablen setzen

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=secure-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

### 2. DNS Records (SPF, DKIM, DMARC)

Für professionelles Email-Versenden konfiguriere:
- **SPF Record:** Verhindert Email-Spoofing
- **DKIM:** Digitale Signatur für Emails
- **DMARC:** Email-Authentifizierungs-Policy

### 3. Email-Service Provider

Empfohlene Anbieter für Production:
- **SendGrid** - 100 Emails/Tag kostenlos
- **AWS SES** - 62,000 Emails/Monat kostenlos
- **Mailgun** - 5,000 Emails/Monat kostenlos
- **Postmark** - Hohe Zustellrate

### 4. Monitoring

Überwache:
- Email-Zustellrate
- Bounce Rate
- Spam-Beschwerden
- Token-Ablauf-Zeiten
- API-Fehlerrate

---

## 📝 Frontend Integration

### React Beispiel

```javascript
// Email Verifikation
async function verifyEmail(token) {
  const response = await fetch(`${API_URL}/api/accounts/verify-email/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    alert('Email erfolgreich verifiziert!');
    // Redirect to login
  } else {
    alert(data.error);
  }
}

// Passwort Reset anfordern
async function requestPasswordReset(email) {
  const response = await fetch(`${API_URL}/api/accounts/request-password-reset/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email })
  });
  
  const data = await response.json();
  alert(data.message);
}

// Neues Passwort setzen
async function resetPassword(token, newPassword) {
  const response = await fetch(`${API_URL}/api/accounts/reset-password/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token,
      new_password: newPassword,
      new_password2: newPassword
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    alert('Passwort erfolgreich zurückgesetzt!');
    // Redirect to login
  } else {
    alert(JSON.stringify(data));
  }
}
```

### URL-Parameter auslesen

```javascript
// Email Verifikation
// URL: http://localhost:3000/verify-email?token=abc123

const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (token) {
  verifyEmail(token);
}

// Passwort Reset
// URL: http://localhost:3000/reset-password?token=xyz789

const resetToken = urlParams.get('token');
if (resetToken) {
  // Zeige Passwort-Reset-Formular an
}
```

---

## ✅ Checkliste

### Vor der Inbetriebnahme

- [ ] SMTP-Credentials in .env konfiguriert
- [ ] Test-Email erfolgreich versendet
- [ ] Frontend URLs korrekt gesetzt
- [ ] Email-Templates getestet
- [ ] Token-Ablaufzeiten angepasst
- [ ] Rate Limiting implementiert
- [ ] HTTPS aktiviert (Production)
- [ ] DNS Records konfiguriert (Production)
- [ ] Monitoring eingerichtet

---

## 🆘 Support

Bei Problemen:
1. Teste SMTP-Konfiguration mit `/api/accounts/test-smtp/`
2. Überprüfe Admin-Panel für Token-Status
3. Checke Terminal/Logs für Fehlermeldungen
4. Teste mit Console-Backend (`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`)

---

**Version:** 1.0  
**Letzte Aktualisierung:** 22.12.2024
