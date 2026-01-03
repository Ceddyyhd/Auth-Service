# 🔐 Auth Service - Vollständige API Dokumentation

**Base URL**: `https://auth.palmdynamicx.de`  
**Version**: 2.0  
**Letzte Aktualisierung**: Januar 2026

---

## 📌 Übersicht

Diese Dokumentation beschreibt **alle** API-Endpunkte des Auth-Service inklusive:
- ✅ Authentifizierung & Registrierung
- ✅ Multi-Factor Authentication (MFA)
- ✅ Single Sign-On (SSO)
- ✅ Social Login (Google, Facebook, GitHub, etc.)
- ✅ E-Mail Verifizierung & Passwort-Reset
- ✅ Lexware-Integration
- ✅ Berechtigungssystem
- ✅ Session Management
- ✅ SMTP-Konfiguration

---

## 🔐 Authentifizierungsmethoden

### 1. JWT Bearer Token
Für authentifizierte Endpunkte:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLC...
```

### 2. API-Key (Erforderlich für ALLE Anfragen)
Jede Anfrage muss einen gültigen API-Key enthalten:
```
X-API-Key: pk_your_api_key_here
```

Optional für erhöhte Sicherheit:
```
X-API-Secret: sk_your_api_secret_here
```

### 3. Session Cookie (für SSO)
```
Cookie: sessionid=xyz123...
```

---

## 🎯 Wichtige Konzepte

### MFA (Multi-Factor Authentication)
- Wenn MFA für einen Benutzer aktiviert ist, erfolgt der Login in **2 Schritten**
- Nach Username/Passwort wird ein zusätzlicher MFA-Token benötigt
- TOTP-Token (6-stellig) oder Backup-Codes können verwendet werden

### Lexware-Integration
- Automatische Kundenkonto-Erstellung wenn:
  - ✅ Vorname + Nachname vorhanden
  - ✅ Vollständige Adresse (Straße, Stadt, PLZ)
- Kundennummer wird im User-Profil gespeichert

### Profil-Vervollständigung
- Websites können erforderliche Felder definieren
- Social Login-Benutzer müssen ggf. Profil vervollständigen
- API gibt fehlende Felder in Response zurück

---

---

## 📋 Inhaltsverzeichnis

1. [Authentifizierung & Registrierung](#authentifizierung--registrierung)
2. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
3. [E-Mail Verifizierung](#e-mail-verifizierung)
4. [Passwort Management](#passwort-management)
5. [Benutzerprofil](#benutzerprofil)
6. [Social Login](#social-login)
7. [Profil-Vervollständigung](#profil-vervollständigung)
8. [Website Management](#website-management)
9. [Single Sign-On (SSO)](#single-sign-on-sso)
10. [Session Management](#session-management)
11. [SMTP-Konfiguration](#smtp-konfiguration)
12. [Fehlerbehandlung](#fehlerbehandlung)
13. [Best Practices](#best-practices)

---

## 📋 Authentifizierung & Registrierung

### 1. Benutzer registrieren
```
POST /api/accounts/register/
```

**Authentifizierung**: Keine (öffentlich)

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "company": "Firma GmbH",
  "date_of_birth": "1990-01-01",
  "website_id": "uuid-der-website"
}
```

**Pflichtfelder**:
- `email` (string)
- `username` (string)
- `password` (string)
- `password2` (string) - muss mit password übereinstimmen
- `website_id` (UUID)

**Optionale Felder** (abhängig von Website-Einstellungen):
- `first_name`, `last_name`, `phone`, `street`, `street_number`, `city`, `postal_code`, `country`, `company`, `date_of_birth`

**Response** (201 Created):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann",
    "profile_completed": true,
    "is_verified": false,
    "lexware_customer_number": 10020
  },
  "tokens": {
    "refresh": "eyJ0eXAi...",
    "access": "eyJ0eXAi..."
  },
  "message": "Benutzer erfolgreich registriert.",
  "verification_email_sent": true,
  "lexware_customer_number": 10020
}
```

**Lexware-Integration**: Wenn Vorname, Nachname und vollständige Adresse (Straße, Stadt, PLZ) vorhanden sind, wird automatisch ein Lexware-Kundenkonto erstellt.

---

### 2. Login
```
POST /api/accounts/login/
```

**Authentifizierung**: Keine (öffentlich)  
**API-Key erforderlich**: ✅ Ja

#### Ohne MFA

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Hinweis**: `username` kann E-Mail oder Username sein

**Response** (200 OK):
```json
{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann",
    "is_verified": true,
    "is_active": true
  }
}
```

#### Mit MFA aktiviert (2-Schritt-Prozess)

**Schritt 1: Initiales Login** (Username + Passwort)

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK - MFA erforderlich):
```json
{
  "mfa_required": true,
  "temp_token": "temporary_session_token_xyz",
  "user_id": "uuid",
  "message": "MFA verification required. Please provide your 6-digit code."
}
```

**Schritt 2: MFA-Token eingeben**

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!",
  "mfa_token": "123456"
}
```

**Alternativ mit Backup-Code**:
```json
{
  "username": "user@example.com",
  "password": "SecurePass123!",
  "mfa_token": "ABC123DEF456"
}
```

**Response** (200 OK - Login erfolgreich):
```json
{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann",
    "is_verified": true,
    "is_active": true,
    "mfa_enabled": true
  },
  "message": "Successfully logged in with MFA"
}
```

**Response** (401 Unauthorized - Falscher MFA-Token):
```json
{
  "error": "Invalid MFA token",
  "message": "The MFA token you provided is invalid or has expired."
}
```

**Frontend-Beispiel**:
```javascript
async function login(username, password, mfaToken = null) {
  const payload = {
    username,
    password
  };
  
  // Wenn MFA-Token vorhanden, hinzufügen
  if (mfaToken) {
    payload.mfa_token = mfaToken;
  }
  
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  
  // Prüfen ob MFA erforderlich
  if (data.mfa_required) {
    // MFA-Formular anzeigen
    const mfaCode = await showMFAPrompt();
    // Erneut aufrufen mit MFA-Token
    return login(username, password, mfaCode);
  }
  
  // Login erfolgreich - Token speichern
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}
```

---

### 3. Token erneuern
```
POST /api/accounts/token/refresh/
```

**Authentifizierung**: Keine

**Request Body**:
```json
{
  "refresh": "eyJ0eXAi..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi..."
}
```

---

### 4. Logout
```
POST /api/accounts/logout/
```

**Authentifizierung**: Bearer Token erforderlich  
**Header**: `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "refresh": "eyJ0eXAi..."
}
```

**Response** (200 OK):
```json
{
  "message": "Erfolgreich abgemeldet."
}
```

---

## 📧 E-Mail Verifizierung

### 5. Verifizierungs-E-Mail erneut senden
```
POST /api/accounts/resend-verification/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Verifizierungs-E-Mail wurde erneut gesendet."
}
```

---

### 6. E-Mail verifizieren
```
POST /api/accounts/verify-email/
```

**Authentifizierung**: Keine

**Request Body**:
```json
{
  "token": "verification-token-from-email"
}
```

**Response** (200 OK):
```json
{
  "message": "E-Mail erfolgreich verifiziert.",
  "email_verified": true
}
```

---

## 🔑 Passwort Management

### 7. Passwort zurücksetzen (Anfrage)
```
POST /api/accounts/request-password-reset/
```

**Authentifizierung**: Keine

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Passwort-Reset-E-Mail wurde gesendet."
}
```

---

### 8. Passwort zurücksetzen (Bestätigung)
```
POST /api/accounts/reset-password/
```

**Authentifizierung**: Keine

**Request Body**:
```json
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!",
  "new_password2": "NewSecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Passwort erfolgreich zurückgesetzt."
}
```

---

### 9. Passwort ändern
```
POST /api/accounts/change-password/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password2": "NewPass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Passwort erfolgreich geändert."
}
```

---

## 👤 Benutzerprofil

### 10. Profil abrufen
```
GET /api/accounts/profile/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789",
  "full_name": "Max Mustermann",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "company": "Firma GmbH",
  "date_of_birth": "1990-01-01",
  "profile_completed": true,
  "is_verified": true,
  "is_active": true,
  "date_joined": "2025-12-26T10:00:00Z",
  "last_login": "2025-12-26T15:30:00Z",
  "lexware_contact_id": "uuid",
  "lexware_customer_number": 10020
}
```

---

### 11. Profil aktualisieren
```
PUT /api/accounts/profile/
PATCH /api/accounts/profile/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body** (alle Felder optional bei PATCH):
```json
{
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789",
  "street": "Neue Straße",
  "street_number": "456",
  "city": "München",
  "postal_code": "80331",
  "country": "Deutschland",
  "company": "Neue Firma GmbH"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  ...
}
```

---

## 🔗 Social Login

### 12. Social Login (Google, Facebook, GitHub, etc.)
```
POST /api/accounts/social-login/
```

**Authentifizierung**: Keine

**Request Body**:
```json
{
  "provider": "google",
  "provider_user_id": "1234567890",
  "email": "user@gmail.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  "avatar_url": "https://example.com/avatar.jpg",
  "access_token": "provider_access_token"
}
```

**Provider-Optionen**: `google`, `facebook`, `github`, `microsoft`, `apple`

**Response** (201 Created oder 200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "username": "user",
    "first_name": "Max",
    "last_name": "Mustermann"
  },
  "social_account": {
    "id": "uuid",
    "provider": "google",
    "email": "user@gmail.com"
  },
  "tokens": {
    "refresh": "eyJ0eXAi...",
    "access": "eyJ0eXAi..."
  },
  "created": true,
  "profile_completed": false,
  "lexware_ready": false,
  "lexware_missing_fields": ["Straße", "Stadt", "PLZ"],
  "lexware_info": "Profil unvollständig für Kundenkonto. Fehlende Felder: Straße, Stadt, PLZ",
  "message": "Erfolgreich mit Social Login angemeldet."
}
```

---

### 13. Social Accounts anzeigen
```
GET /api/accounts/social-accounts/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
{
  "social_accounts": [
    {
      "id": "uuid",
      "provider": "google",
      "provider_display": "Google",
      "email": "user@gmail.com",
      "first_name": "Max",
      "last_name": "Mustermann",
      "avatar_url": "https://...",
      "created_at": "2025-12-26T10:00:00Z"
    }
  ]
}
```

---

### 14. Social Account entfernen
```
DELETE /api/accounts/social-accounts/{provider}/
```

**Authentifizierung**: Bearer Token erforderlich

**URL Parameter**: `provider` - z.B. `google`, `facebook`, `github`

**Response** (200 OK):
```json
{
  "message": "google Account erfolgreich entfernt."
}
```

---

## 📝 Profil-Vervollständigung

### 15. Profil vervollständigen
```
POST /api/accounts/complete-profile/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "profile_completed": true,
    "lexware_customer_number": 10020
  },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_created": true,
  "lexware_customer_number": 10020
}
```

**Wichtig**: Wenn Vorname, Nachname und vollständige Adresse vorhanden sind, wird automatisch ein Lexware-Kundenkonto erstellt!

---

### 16. Profil-Vollständigkeit prüfen
```
GET /api/accounts/check-profile-completion/
POST /api/accounts/check-profile-completion/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body** (optional):
```json
{
  "website_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "profile_completed": false,
  "missing_fields": ["Straße", "Stadt", "PLZ"],
  "has_lexware_contact": false,
  "lexware_customer_number": null,
  "user": { ... }
}
```

**Mit website_id** (zusätzlich):
```json
{
  "profile_completed": false,
  "missing_fields": ["Straße", "Stadt", "PLZ"],
  "has_lexware_contact": false,
  "lexware_customer_number": null,
  "user": { ... },
  "website_check": {
    "website_id": "uuid",
    "website_name": "Meine Website",
    "profile_completed": false,
    "missing_fields": ["phone", "street"],
    "required_fields": {
      "require_first_name": true,
      "require_last_name": true,
      "require_phone": true,
      "require_address": true
    }
  }
}
```

---

## 🌐 Website Management

### 17. Websites auflisten
```
GET /api/accounts/websites/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "name": "Meine Website",
    "domain": "example.com",
    "callback_url": "https://example.com/auth/callback",
    "is_active": true,
    "auto_register_users": false,
    "created_at": "2025-12-26T10:00:00Z"
  }
]
```

---

### 18. Website erstellen
```
POST /api/accounts/websites/
```

**Authentifizierung**: Bearer Token erforderlich (Admin/Staff)

**Request Body**:
```json
{
  "name": "Meine Website",
  "domain": "example.com",
  "callback_url": "https://example.com/auth/callback",
  "allowed_origins": ["https://example.com", "https://www.example.com"],
  "is_active": true,
  "auto_register_users": false,
  "require_first_name": true,
  "require_last_name": true,
  "require_phone": false,
  "require_address": true,
  "require_email_verification": true
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "Meine Website",
  "domain": "example.com",
  "api_key": "pk_xxx...",
  "api_secret": "sk_xxx...",
  "client_id": "client_xxx...",
  "client_secret": "xxx...",
  "callback_url": "https://example.com/auth/callback",
  "allowed_origins": ["https://example.com"],
  "is_active": true,
  "created_at": "2025-12-26T10:00:00Z"
}
```

**Wichtig**: API Credentials werden automatisch generiert!

---

### 19. Website-Details abrufen
```
GET /api/accounts/websites/{website_id}/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "Meine Website",
  "domain": "example.com",
  "callback_url": "https://example.com/auth/callback",
  "is_active": true,
  "require_first_name": true,
  "require_last_name": true,
  "require_phone": false,
  "require_address": true,
  "created_at": "2025-12-26T10:00:00Z"
}
```

---

### 20. Website-Pflichtfelder abrufen
```
GET /api/accounts/websites/{website_id}/required-fields/
```

**Authentifizierung**: Keine

**Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "Meine Website",
  "domain": "example.com",
  "require_first_name": true,
  "require_last_name": true,
  "require_phone": false,
  "require_address": true,
  "require_date_of_birth": false,
  "require_company": false
}
```

---

---

## 🎭 Multi-Factor Authentication (MFA)

Das MFA-System bietet TOTP-basierte Zwei-Faktor-Authentifizierung mit:
- ✅ QR-Code für Authenticator-Apps (Google Authenticator, Microsoft Authenticator, Authy)
- ✅ 10 Backup-Codes für Notfälle
- ✅ Automatische Integration in Login-Flow
- ✅ Sicheres Deaktivieren (Passwort + MFA-Token erforderlich)

### 21. MFA aktivieren
```
POST /api/accounts/mfa/enable/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Request Body**: Leer `{}`

**Response** (200 OK):
```json
{
  "message": "MFA setup initiated. Please scan the QR code with your authenticator app and verify.",
  "secret_key": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "backup_codes": [
    "A1B2C3D4",
    "E5F6G7H8",
    "I9J0K1L2",
    "M3N4O5P6",
    "Q7R8S9T0",
    "U1V2W3X4",
    "Y5Z6A7B8",
    "C9D0E1F2",
    "G3H4I5J6",
    "K7L8M9N0"
  ],
  "manual_entry_key": "JBSWY3DPEHPK3PXP"
}
```

**Wichtig**: 
- ⚠️ MFA ist nach diesem Schritt noch NICHT aktiv
- 💾 Backup-Codes sicher speichern (werden nur einmal angezeigt!)
- 📱 QR-Code mit Authenticator-App scannen
- ✅ Dann Endpoint `/mfa/verify-setup/` aufrufen um MFA zu aktivieren

**Frontend-Beispiel**:
```javascript
async function enableMFA(accessToken) {
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/mfa/enable/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'X-API-Key': 'YOUR_API_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  
  const data = await response.json();
  
  // QR-Code anzeigen
  document.getElementById('qrCode').src = data.qr_code;
  
  // Backup-Codes anzeigen (zum Herunterladen/Drucken)
  displayBackupCodes(data.backup_codes);
  
  // Manueller Key für Eingabe ohne QR-Scanner
  document.getElementById('manualKey').textContent = data.manual_entry_key;
  
  return data;
}
```

---

### 22. MFA-Setup verifizieren
```
POST /api/accounts/mfa/verify-setup/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Beschreibung**: Aktiviert MFA durch Bestätigung eines TOTP-Tokens. Erst nach erfolgreicher Verifizierung ist MFA aktiv.

**Request Body**:
```json
{
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "MFA has been successfully enabled",
  "backup_codes_count": 10
}
```

**Response** (400 Bad Request - Ungültiger Token):
```json
{
  "error": "Invalid token. Please try again."
}
```

---

### 23. MFA deaktivieren
```
POST /api/accounts/mfa/disable/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Sicherheit**: Erfordert **sowohl Passwort als auch MFA-Token** für maximale Sicherheit

**Request Body**:
```json
{
  "password": "YourCurrentPassword123!",
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "MFA has been successfully disabled"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "Invalid password or MFA token"
}
```

---

### 24. MFA-Status abrufen
```
GET /api/accounts/mfa/status/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Response** (200 OK):
```json
{
  "mfa_enabled": true,
  "activated_at": "2025-12-22T10:30:00Z",
  "last_used": "2026-01-03T18:45:00Z",
  "backup_codes_count": 8
}
```

---

### 25. MFA-Token verifizieren
```
POST /api/accounts/mfa/verify/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Beschreibung**: Verifiziert einen MFA-Token ohne Zustandsänderung. Nützlich für Re-Authentifizierung oder Testing.

**Request Body**:
```json
{
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

**Response** (400 Bad Request):
```json
{
  "valid": false,
  "error": "Invalid or expired token"
}
```

---

### 26. Backup-Codes neu generieren
```
POST /api/accounts/mfa/backup-codes/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Beschreibung**: Generiert 10 neue Backup-Codes. **Alte Codes werden ungültig!**

**Request Body**:
```json
{
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "Backup codes have been regenerated",
  "backup_codes": [
    "X1Y2Z3A4",
    "B5C6D7E8",
    "F9G0H1I2",
    "J3K4L5M6",
    "N7O8P9Q0",
    "R1S2T3U4",
    "V5W6X7Y8",
    "Z9A0B1C2",
    "D3E4F5G6",
    "H7I8J9K0"
  ]
}
```

**Wichtig**: Alte Backup-Codes sind nach diesem Vorgang ungültig!

---

### MFA Best Practices

#### Für Benutzer:
1. 💾 **Backup-Codes sicher aufbewahren**: Offline speichern (z.B. ausdrucken)
2. 📱 **Mehrere Geräte**: Authenticator auf mehreren Geräten einrichten
3. 🔄 **Backup-Codes erneuern**: Wenn alle verwendet oder kompromittiert
4. 🔐 **Niemals teilen**: MFA-Tokens oder Backup-Codes niemals weitergeben

#### Für Entwickler:
1. ⏱️ **Time Sync**: TOTP-Token sind zeitbasiert (30 Sekunden Fenster)
2. 🔄 **Retry-Logik**: Benutzer können mehrmals versuchen
3. 📱 **QR-Code Alternative**: Immer manuelle Eingabe-Option anbieten
4. 💬 **Klare Fehlermeldungen**: "Token ungültig" statt generische Fehler

---

## 📊 Sessions

### 27. Aktive Sessions anzeigen
```
GET /api/accounts/sessions/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Response** (200 OK):
```json
[
  {
    "id": "uuid",
    "website": {
      "id": "uuid",
      "name": "Meine Website",
      "domain": "example.com"
    },
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "is_active": true,
    "created_at": "2025-12-26T10:00:00Z",
    "last_activity": "2025-12-26T15:30:00Z",
    "expires_at": "2025-12-27T10:00:00Z"
  }
]
```

---

## 🔐 Single Sign-On (SSO)

Das SSO-System ermöglicht nahtlose Anmeldung über mehrere Websites hinweg.

### 28. SSO Status prüfen
```
POST /api/accounts/sso/status/
```

**Authentifizierung**: Keine (öffentlich)  
**API-Key erforderlich**: ✅ Ja  
**Session Cookie**: Optional

**Request Body**:
```json
{
  "website_id": "your-website-uuid"
}
```

**Response (Benutzer angemeldet):**
```json
{
  "sso_available": true,
  "authenticated": true,
  "has_access": true,
  "user_id": "user-uuid",
  "email": "user@example.com"
}
```

**Response (Benutzer nicht angemeldet):**
```json
{
  "sso_available": false,
  "authenticated": false,
  "has_access": false
}
```

---

### 29. SSO initiieren
```
GET /api/accounts/sso/initiate/
```

**Authentifizierung**: Keine (öffentlich)  
**API-Key erforderlich**: ✅ Ja  
**Session Cookie**: Erforderlich

**Query Parameters:**
- `website_id` (UUID): ID der Website
- `return_url` (string): URL für Redirect nach SSO

**Request:**
```bash
curl -X GET "https://auth.palmdynamicx.de/api/accounts/sso/initiate/?website_id=YOUR_WEBSITE_ID&return_url=https://yourwebsite.com/auth/callback" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Cookie: sessionid=YOUR_SESSION_COOKIE"
```

**Response (User angemeldet):**
```json
{
  "authenticated": true,
  "sso_token": "very_long_secure_token_here",
  "redirect_url": "https://yourwebsite.com/auth/callback?sso_token=very_long_secure_token_here",
  "expires_in": 300
}
```

**Response (User NICHT angemeldet):**
```json
{
  "authenticated": false,
  "login_url": "https://auth.palmdynamicx.de/api/accounts/login/?redirect=sso",
  "message": "User must login first"
}
```

---

### 30. SSO-Token austauschen
```
POST /api/accounts/sso/exchange/
```

**Authentifizierung**: Keine (öffentlich)  
**API-Key erforderlich**: ✅ Ja

**Beschreibung**: Tauscht einen SSO-Token gegen JWT Access/Refresh Tokens

**Request Body**:
```json
{
  "token": "sso-token-xxx",
  "website_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "Max",
    "last_name": "Mustermann"
  }
}
```

**Response** (400 Bad Request):
```json
{
  "error": "Invalid or expired SSO token"
}
```

---

### 31. SSO-Token Status prüfen
```
GET /api/accounts/sso/status/?token=xxx
```

**Authentifizierung**: Keine  
**API-Key erforderlich**: ✅ Ja

**Query Parameters:**
- `token` (string): SSO-Token

**Response** (200 OK):
```json
{
  "valid": true,
  "user_id": "uuid",
  "website_id": "uuid",
  "expires_at": "2026-01-03T10:05:00Z"
}
```

**Response** (Token ungültig):
```json
{
  "valid": false,
  "error": "Token expired or invalid"
}
```

---

### 32. SSO Logout
```
POST /api/accounts/sso/logout/
```

**Authentifizierung**: Session Cookie erforderlich  
**API-Key erforderlich**: ✅ Ja

**Beschreibung**: Meldet Benutzer von allen SSO-Sessions ab

**Request Body**: Leer `{}`

**Response** (200 OK):
```json
{
  "message": "Successfully logged out from all SSO sessions"
}
```

---

### SSO Flow Beispiel

**Schritt 1: Benutzer besucht Website B**
```javascript
// Website B prüft, ob User bereits Session hat
if (!hasLocalSession()) {
  // Prüfe SSO-Status
  const ssoStatus = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/status/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify({
      website_id: 'YOUR_WEBSITE_ID'
    }),
    credentials: 'include' // Wichtig für Session Cookie
  });
  
  const data = await ssoStatus.json();
  
  if (data.sso_available) {
    // SSO ist möglich - weiter zu Schritt 2
    initiateSSO();
  } else {
    // Redirect zu Login
    window.location = 'https://auth.palmdynamicx.de/login';
  }
}
```

**Schritt 2: SSO initiieren**
```javascript
async function initiateSSO() {
  const returnUrl = 'https://yourwebsite.com/auth/callback';
  
  const response = await fetch(
    `https://auth.palmdynamicx.de/api/accounts/sso/initiate/?website_id=YOUR_WEBSITE_ID&return_url=${returnUrl}`,
    {
      headers: {
        'X-API-Key': 'YOUR_API_KEY'
      },
      credentials: 'include' // Session Cookie
    }
  );
  
  const data = await response.json();
  
  if (data.authenticated) {
    // Redirect zur Callback-URL mit SSO-Token
    window.location = data.redirect_url;
  }
}
```

**Schritt 3: SSO-Token austauschen (auf Callback-Page)**
```javascript
// Auf https://yourwebsite.com/auth/callback?sso_token=xxx
const urlParams = new URLSearchParams(window.location.search);
const ssoToken = urlParams.get('sso_token');

if (ssoToken) {
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/exchange/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify({
      token: ssoToken,
      website_id: 'YOUR_WEBSITE_ID'
    })
  });
  
  const data = await response.json();
  
  // Token speichern und User ist eingeloggt!
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  // Redirect zu Dashboard
  window.location = '/dashboard';
}
```

---

## 🔍 Zugriffsprüfung

### 33. Zugriff verifizieren
```
POST /api/accounts/verify-access/
```

**Authentifizierung**: Bearer Token erforderlich  
**API-Key erforderlich**: ✅ Ja

**Request Body**:
```json
{
  "website_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "has_access": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username"
  },
  "website": {
    "id": "uuid",
    "name": "Meine Website",
    "domain": "example.com"
  }
}
```

**Response** (403 Forbidden):
```json
{
  "has_access": false,
  "error": "User does not have access to this website"
}
```

---

## 📱 SMTP Konfiguration

### 34. SMTP testen
```
POST /api/accounts/test-smtp/
```

**Authentifizierung**: Bearer Token erforderlich (Admin/Staff)  
**API-Key erforderlich**: ✅ Ja

**Request Body**:
```json
{
  "email": "test@example.com"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Test-E-Mail erfolgreich gesendet an test@example.com"
}
```

**Response** (500 Internal Server Error):
```json
{
  "success": false,
  "error": "SMTP connection failed",
  "details": "Connection refused by server"
}
```

---

### 35. SMTP-Konfiguration abrufen
```
GET /api/accounts/smtp-config/
```

**Authentifizierung**: Bearer Token erforderlich (Admin/Staff)  
**API-Key erforderlich**: ✅ Ja

**Response** (200 OK):
```json
{
  "email_host": "smtp.zoho.eu",
  "email_port": 465,
  "email_use_ssl": true,
  "email_use_tls": false,
  "email_from": "noreply@palmdynamicx.de"
}
```

**Hinweis**: Sensible Daten (Passwörter) werden nicht zurückgegeben

---

## ⚠️ Fehlerbehandlung

Alle Endpoints können folgende Fehler zurückgeben:

### 400 Bad Request - Validierungsfehler
```json
{
  "error": "Validation error",
  "details": {
    "email": ["Dieses Feld ist erforderlich."],
    "password": ["Passwort muss mindestens 8 Zeichen lang sein."]
  }
}
```

**Häufige Ursachen:**
- Fehlende Pflichtfelder
- Ungültiges Format (z.B. E-Mail)
- Passwörter stimmen nicht überein
- Zu schwaches Passwort

---

### 401 Unauthorized - Fehlende oder ungültige Authentifizierung
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "authentication_failed"
}
```

**Häufige Ursachen:**
- Kein Bearer Token im Header
- Token abgelaufen
- Ungültiger Token
- Falscher Username/Passwort

**MFA-spezifisch:**
```json
{
  "error": "Invalid MFA token",
  "message": "The MFA token you provided is invalid or has expired.",
  "mfa_required": true
}
```

**Lösung:**
```javascript
// Token erneuern
const refreshResponse = await fetch('/api/accounts/token/refresh/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    refresh: localStorage.getItem('refresh_token')
  })
});

const data = await refreshResponse.json();
localStorage.setItem('access_token', data.access);
```

---

### 403 Forbidden - Keine Berechtigung
```json
{
  "detail": "You do not have permission to perform this action.",
  "code": "permission_denied"
}
```

**Häufige Ursachen:**
- Benutzer ist nicht Admin/Staff (z.B. SMTP-Konfiguration)
- Kein Zugriff auf angeforderte Website
- E-Mail nicht verifiziert (falls erforderlich)
- MFA erforderlich aber nicht durchgeführt

---

### 404 Not Found
```json
{
  "detail": "Not found.",
  "code": "not_found"
}
```

**Häufige Ursachen:**
- Ungültige Website-ID
- Benutzer existiert nicht
- SSO-Token nicht gefunden

---

### 429 Too Many Requests - Rate Limit
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds.",
  "code": "throttled"
}
```

**Rate Limits:**
- Standard: 100 Requests/Minute pro IP
- Login: 5 Versuche/15 Minuten
- Passwort-Reset: 3 Anfragen/Stunde
- MFA-Verifizierung: 10 Versuche/5 Minuten

**Lösung:**
```javascript
// Retry-Logik mit exponential backoff
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(url, options);
    
    if (response.status !== 429) {
      return response;
    }
    
    // Warte 2^i Sekunden
    const waitTime = Math.pow(2, i) * 1000;
    await new Promise(resolve => setTimeout(resolve, waitTime));
  }
  
  throw new Error('Max retries exceeded');
}
```

---

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Ein unerwarteter Fehler ist aufgetreten.",
  "request_id": "abc-123-def-456"
}
```

**Mögliche Ursachen:**
- Datenbankfehler
- Lexware API nicht erreichbar
- SMTP-Server Probleme
- Konfigurationsfehler

**Hinweis:** Bei 500-Fehlern den Support mit der `request_id` kontaktieren

---

### Fehlerbehandlung Best Practices

#### 1. Globaler Error Handler
```javascript
class AuthAPIClient {
  async request(endpoint, options = {}) {
    const response = await fetch(`https://auth.palmdynamicx.de${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
        ...(options.headers || {})
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new AuthAPIError(response.status, data);
    }
    
    return data;
  }
}

class AuthAPIError extends Error {
  constructor(status, data) {
    super(data.error || data.detail || 'API Error');
    this.status = status;
    this.data = data;
    this.name = 'AuthAPIError';
  }
  
  isValidationError() {
    return this.status === 400 && this.data.details;
  }
  
  isAuthError() {
    return this.status === 401;
  }
  
  isMFARequired() {
    return this.data.mfa_required === true;
  }
  
  isRateLimited() {
    return this.status === 429;
  }
}
```

#### 2. Benutzerfreundliche Fehlermeldungen
```javascript
function getErrorMessage(error) {
  if (error.isValidationError()) {
    const fields = Object.keys(error.data.details);
    return `Bitte überprüfe folgende Felder: ${fields.join(', ')}`;
  }
  
  if (error.isMFARequired()) {
    return 'Bitte gib deinen 6-stelligen Authentifizierungscode ein.';
  }
  
  if (error.isRateLimited()) {
    return 'Zu viele Anfragen. Bitte versuche es in wenigen Minuten erneut.';
  }
  
  if (error.status === 401) {
    return 'Deine Sitzung ist abgelaufen. Bitte melde dich erneut an.';
  }
  
  return 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.';
}
```

#### 3. Token Refresh Handling
```javascript
async function fetchWithAuth(url, options = {}) {
  let accessToken = localStorage.getItem('access_token');
  
  // Erste Anfrage mit aktuellem Token
  let response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'X-API-Key': 'YOUR_API_KEY',
      ...options.headers
    }
  });
  
  // Wenn 401, versuche Token zu erneuern
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const refreshResponse = await fetch(
      'https://auth.palmdynamicx.de/api/accounts/token/refresh/',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'YOUR_API_KEY'
        },
        body: JSON.stringify({ refresh: refreshToken })
      }
    );
    
    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      localStorage.setItem('access_token', data.access);
      
      // Wiederhole ursprüngliche Anfrage
      response = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${data.access}`,
          'X-API-Key': 'YOUR_API_KEY',
          ...options.headers
        }
      });
    } else {
      // Refresh fehlgeschlagen - logout erforderlich
      localStorage.clear();
      window.location = '/login';
      throw new Error('Session expired');
    }
  }
  
  return response;
}
```

---

## 🔑 Authentifizierung

### JWT Bearer Token
Die meisten Endpoints benötigen einen Bearer Token im Authorization Header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### API-Key (Erforderlich für ALLE Anfragen)
```
X-API-Key: pk_your_api_key_here
```

### Token-Lebensdauer
- **Access Token**: 1 Stunde
- **Refresh Token**: 7 Tage
- **SSO Token**: 5 Minuten
- **Email Verification Token**: 24 Stunden
- **Password Reset Token**: 1 Stunde

### Token erneuern
Wenn der Access Token abläuft, verwende den Refresh Token um einen neuen zu erhalten:

```
POST /api/accounts/token/refresh/
Body: { "refresh": "eyJ0eXAi..." }
```

---

## 🎯 Best Practices

### 1. Sicherheit

#### ✅ API-Keys sicher aufbewahren
```javascript
// ❌ Falsch - API-Key im Frontend-Code
const API_KEY = 'pk_12345...';

// ✅ Richtig - API-Key aus Umgebungsvariablen
const API_KEY = process.env.REACT_APP_API_KEY;
```

#### ✅ Tokens sicher speichern
```javascript
// ❌ Falsch - Token im localStorage (XSS-anfällig)
localStorage.setItem('access_token', token);

// ✅ Besser - HttpOnly Cookies (serverseitig setzen)
// Oder: Secure localStorage mit XSS-Schutz

// ✅ Am besten - Token im Memory + Refresh Token im HttpOnly Cookie
class TokenManager {
  constructor() {
    this.accessToken = null;
  }
  
  setAccessToken(token) {
    this.accessToken = token;
  }
  
  getAccessToken() {
    return this.accessToken;
  }
  
  clearTokens() {
    this.accessToken = null;
  }
}
```

#### ✅ HTTPS verwenden
```javascript
// ❌ Falsch
const API_URL = 'http://auth.palmdynamicx.de';

// ✅ Richtig
const API_URL = 'https://auth.palmdynamicx.de';
```

#### ✅ CORS-Header beachten
Stelle sicher, dass deine Domain in `allowed_origins` der Website-Konfiguration eingetragen ist.

---

### 2. MFA Implementierung

#### ✅ Login-Flow mit MFA
```javascript
async function handleLogin(username, password) {
  try {
    // Schritt 1: Login-Versuch
    const response = await authClient.login(username, password);
    
    // Prüfe ob MFA erforderlich
    if (response.mfa_required) {
      // Zeige MFA-Input-Feld
      showMFAInput();
      
      // Warte auf Benutzereingabe
      const mfaToken = await getMFATokenFromUser();
      
      // Schritt 2: Login mit MFA
      return await authClient.login(username, password, mfaToken);
    }
    
    // Login erfolgreich ohne MFA
    return response;
    
  } catch (error) {
    if (error.isMFARequired()) {
      // MFA-Token war falsch, nochmal versuchen
      showError('Ungültiger Code. Bitte versuche es erneut.');
      return handleLogin(username, password);
    }
    
    throw error;
  }
}
```

#### ✅ MFA-Setup UX
```javascript
async function setupMFA() {
  // 1. MFA aktivieren
  const setup = await authClient.enableMFA();
  
  // 2. QR-Code anzeigen
  document.getElementById('qr-code').src = setup.qr_code;
  
  // 3. Backup-Codes zum Download anbieten
  offerBackupCodesDownload(setup.backup_codes);
  
  // 4. Manuelle Eingabe-Option
  document.getElementById('manual-key').textContent = setup.manual_entry_key;
  
  // 5. Verifizierung
  const code = await promptForCode('Gib den 6-stelligen Code aus deiner App ein:');
  
  try {
    await authClient.verifyMFASetup(code);
    showSuccess('MFA erfolgreich aktiviert! 🎉');
  } catch (error) {
    showError('Ungültiger Code. Bitte versuche es erneut.');
  }
}

function offerBackupCodesDownload(codes) {
  const text = `Auth-Service Backup-Codes\n\n${codes.join('\n')}\n\nSpeichere diese Codes sicher!`;
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = 'backup-codes.txt';
  link.click();
}
```

---

### 3. SSO Implementierung

#### ✅ Automatisches SSO bei Seitenaufruf
```javascript
// Bei Seitenaufruf prüfen, ob SSO verfügbar ist
async function initAuth() {
  // Prüfe lokale Session
  const localToken = tokenManager.getAccessToken();
  
  if (localToken && !isTokenExpired(localToken)) {
    // Lokale Session vorhanden
    return true;
  }
  
  // Keine lokale Session - versuche SSO
  try {
    const ssoStatus = await checkSSOStatus();
    
    if (ssoStatus.sso_available) {
      // SSO verfügbar - hole Token
      await performSSO();
      return true;
    }
  } catch (error) {
    console.log('SSO not available');
  }
  
  // Weder lokale Session noch SSO - redirect zu Login
  redirectToLogin();
  return false;
}

async function checkSSOStatus() {
  return await fetch('https://auth.palmdynamicx.de/api/accounts/sso/status/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      website_id: WEBSITE_ID
    }),
    credentials: 'include' // Wichtig für Session-Cookie
  });
}

async function performSSO() {
  const currentUrl = window.location.href;
  const callbackUrl = `${window.location.origin}/auth/callback`;
  
  // Initiiere SSO
  const response = await fetch(
    `https://auth.palmdynamicx.de/api/accounts/sso/initiate/?website_id=${WEBSITE_ID}&return_url=${callbackUrl}`,
    {
      headers: { 'X-API-Key': API_KEY },
      credentials: 'include'
    }
  );
  
  const data = await response.json();
  
  if (data.authenticated) {
    // Redirect zur Callback-URL
    window.location = data.redirect_url;
  } else {
    // Nicht angemeldet - redirect zu Login
    window.location = data.login_url;
  }
}
```

---

### 4. Profil-Vervollständigung

#### ✅ Nach Social Login prüfen
```javascript
async function handleSocialLogin(provider, providerData) {
  const response = await authClient.socialLogin({
    provider,
    provider_user_id: providerData.id,
    email: providerData.email,
    first_name: providerData.given_name,
    last_name: providerData.family_name,
    avatar_url: providerData.picture
  });
  
  // Tokens speichern
  tokenManager.setAccessToken(response.tokens.access);
  
  // Prüfe ob Profil vervollständigt werden muss
  if (!response.profile_completed) {
    // Zeige Profil-Vervollständigungs-Formular
    showProfileCompletionForm(response.lexware_missing_fields);
  } else {
    // Profil vollständig - weiter zur App
    redirectToDashboard();
  }
}

async function completeProfile(profileData) {
  try {
    const response = await authClient.completeProfile(profileData);
    
    if (response.lexware_created) {
      showSuccess(`Profil vervollständigt! Deine Kundennummer: ${response.lexware_customer_number}`);
    } else if (response.lexware_info) {
      showInfo(response.lexware_info);
    }
    
    redirectToDashboard();
    
  } catch (error) {
    showError('Fehler beim Vervollständigen des Profils');
  }
}
```

---

### 5. Fehlerbehandlung & Retry-Logik

#### ✅ Automatisches Token-Refresh
```javascript
class AuthAPIClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'https://auth.palmdynamicx.de';
    this.refreshPromise = null;
  }
  
  async request(endpoint, options = {}) {
    let accessToken = tokenManager.getAccessToken();
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    // Token abgelaufen - refresh
    if (response.status === 401) {
      // Verhindere mehrfache Refresh-Requests
      if (!this.refreshPromise) {
        this.refreshPromise = this.refreshToken();
      }
      
      await this.refreshPromise;
      this.refreshPromise = null;
      
      // Wiederhole ursprüngliche Anfrage
      return this.request(endpoint, options);
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new AuthAPIError(response.status, data);
    }
    
    return data;
  }
  
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch(`${this.baseURL}/api/accounts/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (!response.ok) {
      // Refresh fehlgeschlagen - logout
      this.logout();
      throw new Error('Session expired');
    }
    
    const data = await response.json();
    tokenManager.setAccessToken(data.access);
    localStorage.setItem('refresh_token', data.refresh);
  }
  
  logout() {
    tokenManager.clearTokens();
    localStorage.clear();
    window.location = '/login';
  }
}
```

---

### 6. Performance & Caching

#### ✅ User-Profil cachen
```javascript
class UserCache {
  constructor() {
    this.user = null;
    this.cacheTime = null;
    this.cacheDuration = 5 * 60 * 1000; // 5 Minuten
  }
  
  async getUser(forceRefresh = false) {
    const now = Date.now();
    
    // Cache noch gültig?
    if (!forceRefresh && this.user && this.cacheTime && (now - this.cacheTime < this.cacheDuration)) {
      return this.user;
    }
    
    // Cache abgelaufen oder nicht vorhanden - neu laden
    this.user = await authClient.getProfile();
    this.cacheTime = now;
    
    return this.user;
  }
  
  invalidate() {
    this.user = null;
    this.cacheTime = null;
  }
  
  updateUser(updatedData) {
    this.user = { ...this.user, ...updatedData };
    this.cacheTime = Date.now();
  }
}

const userCache = new UserCache();

// Verwendung
const user = await userCache.getUser(); // Aus Cache wenn vorhanden
const freshUser = await userCache.getUser(true); // Immer neu laden

// Nach Profil-Update
await authClient.updateProfile(newData);
userCache.updateUser(newData); // Cache aktualisieren
```

---

### 7. Logging & Monitoring

#### ✅ Request-Logging
```javascript
class AuthAPIClient {
  async request(endpoint, options = {}) {
    const requestId = generateUUID();
    const startTime = Date.now();
    
    console.log(`[${requestId}] ${options.method || 'GET'} ${endpoint}`);
    
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'X-Request-ID': requestId,
          ...this.getDefaultHeaders(),
          ...options.headers
        }
      });
      
      const duration = Date.now() - startTime;
      console.log(`[${requestId}] ${response.status} in ${duration}ms`);
      
      // Bei Fehler zusätzlich loggen
      if (!response.ok) {
        const data = await response.json();
        console.error(`[${requestId}] Error:`, data);
        
        // Optional: An Monitoring-Service senden
        if (window.analytics) {
          window.analytics.track('API Error', {
            requestId,
            endpoint,
            status: response.status,
            error: data.error || data.detail,
            duration
          });
        }
      }
      
      return response;
      
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(`[${requestId}] Network error after ${duration}ms:`, error);
      
      // Network-Fehler tracken
      if (window.analytics) {
        window.analytics.track('API Network Error', {
          requestId,
          endpoint,
          error: error.message,
          duration
        });
      }
      
      throw error;
    }
  }
}
```

---

## 🎯 Wichtige Hinweise

### Lexware-Integration
Ein Lexware-Kundenkonto wird automatisch erstellt wenn:
- ✅ Vorname vorhanden
- ✅ Nachname vorhanden
- ✅ Straße vorhanden
- ✅ Stadt vorhanden
- ✅ PLZ vorhanden

Fehlende Felder werden in der Response angezeigt:
```json
{
  "lexware_ready": false,
  "lexware_missing_fields": ["Straße", "Stadt", "PLZ"],
  "lexware_info": "Profil unvollständig für Kundenkonto. Fehlende Felder: Straße, Stadt, PLZ"
}
```

**Wichtig**: Lexware-Fehler blockieren nicht die Registrierung! Wenn die Lexware-API nicht erreichbar ist, wird der Benutzer trotzdem erstellt.

---

### Rate Limiting
- **Standard**: 100 Requests pro Minute pro IP
- **Login**: 5 Versuche pro 15 Minuten
- **Passwort-Reset**: 3 Anfragen pro Stunde
- **MFA-Verifizierung**: 10 Versuche pro 5 Minuten
- **E-Mail Versand**: 5 E-Mails pro Stunde pro Benutzer

**Response bei Überschreitung**:
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds.",
  "code": "throttled",
  "available_in": 45
}
```

---

### CORS
Alle in `allowed_origins` registrierten Origins sind erlaubt. Stelle sicher, dass deine Domain eingetragen ist:

```python
# Beispiel Website-Konfiguration
{
  "domain": "example.com",
  "allowed_origins": [
    "https://example.com",
    "https://www.example.com",
    "https://app.example.com"
  ]
}
```

---

### Pagination
Listen-Endpoints unterstützen Pagination:
- `?page=2` - Seite 2
- `?page_size=50` - 50 Einträge pro Seite (Standard: 20, Max: 100)

**Beispiel**:
```javascript
const response = await fetch(
  'https://auth.palmdynamicx.de/api/accounts/sessions/?page=2&page_size=50',
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'X-API-Key': API_KEY
    }
  }
);

const data = await response.json();
console.log(data.results); // Array von Sessions
console.log(data.count); // Gesamtanzahl
console.log(data.next); // URL zur nächsten Seite
console.log(data.previous); // URL zur vorherigen Seite
```

---

### Websocket-Unterstützung
Für Echtzeit-Benachrichtigungen (z.B. neue Sessions, MFA-Änderungen):

```javascript
const ws = new WebSocket(`wss://auth.palmdynamicx.de/ws/notifications/?token=${accessToken}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'new_session':
      console.log('Neue Session erstellt:', data.session);
      break;
    case 'mfa_enabled':
      console.log('MFA wurde aktiviert');
      break;
    case 'password_changed':
      console.log('Passwort wurde geändert');
      break;
  }
};
```

---

### Umgebungen
- **Produktion**: `https://auth.palmdynamicx.de`
- **Staging**: `https://staging-auth.palmdynamicx.de` (falls verfügbar)
- **Lokal**: `http://localhost:8000`

---

### Versionierung
Die API verwendet URL-basierte Versionierung. Aktuelle Version: `v1` (implizit)

Bei Breaking Changes wird eine neue Version eingeführt:
- `/api/v1/accounts/...`
- `/api/v2/accounts/...`

Alte Versionen werden mindestens 6 Monate nach Einführung einer neuen Version unterstützt.

---

## 📚 Verwendungsbeispiele

### Beispiel 1: Kompletter Registrierungs-Flow mit MFA
```javascript
class AuthFlow {
  constructor(apiKey) {
    this.client = new AuthAPIClient(apiKey);
  }
  
  async registerWithMFA(userData) {
    // 1. Registrieren
    const registerResponse = await this.client.register({
      email: userData.email,
      username: userData.username,
      password: userData.password,
      password2: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName,
      street: userData.street,
      street_number: userData.streetNumber,
      city: userData.city,
      postal_code: userData.postalCode,
      country: userData.country,
      website_id: userData.websiteId
    });
    
    console.log('Registrierung erfolgreich!');
    if (registerResponse.lexware_customer_number) {
      console.log(`Kundennummer: ${registerResponse.lexware_customer_number}`);
    }
    
    // Tokens speichern
    const accessToken = registerResponse.tokens.access;
    tokenManager.setAccessToken(accessToken);
    localStorage.setItem('refresh_token', registerResponse.tokens.refresh);
    
    // 2. MFA aktivieren
    const mfaSetup = await this.client.enableMFA(accessToken);
    
    // QR-Code anzeigen
    showQRCode(mfaSetup.qr_code);
    showManualKey(mfaSetup.manual_entry_key);
    
    // Backup-Codes zum Download anbieten
    downloadBackupCodes(mfaSetup.backup_codes);
    
    // 3. Warte auf MFA-Token vom Benutzer
    const mfaToken = await promptForMFAToken();
    
    // 4. MFA verifizieren
    try {
      await this.client.verifyMFASetup(accessToken, mfaToken);
      showSuccess('MFA erfolgreich aktiviert! Dein Account ist jetzt geschützt.');
    } catch (error) {
      showError('Ungültiger Code. Bitte versuche es erneut.');
    }
    
    // 5. Weiter zur App
    redirectToDashboard();
  }
}

// Verwendung
const auth = new AuthFlow('pk_your_api_key');

await auth.registerWithMFA({
  email: 'user@example.com',
  username: 'user123',
  password: 'SecurePass123!',
  firstName: 'Max',
  lastName: 'Mustermann',
  street: 'Musterstraße',
  streetNumber: '123',
  city: 'Berlin',
  postalCode: '10115',
  country: 'Deutschland',
  websiteId: 'your-website-uuid'
});
```

---

### Beispiel 2: Social Login mit Profil-Vervollständigung
```javascript
async function handleGoogleLogin() {
  // 1. Google OAuth durchführen (mit Google SDK)
  const googleUser = await googleSignIn();
  
  // 2. Social Login am Auth-Service
  const response = await authClient.socialLogin({
    provider: 'google',
    provider_user_id: googleUser.id,
    email: googleUser.email,
    first_name: googleUser.given_name,
    last_name: googleUser.family_name,
    avatar_url: googleUser.picture
  });
  
  // Tokens speichern
  tokenManager.setAccessToken(response.tokens.access);
  localStorage.setItem('refresh_token', response.tokens.refresh);
  
  // 3. Prüfe ob Profil vollständig
  if (!response.profile_completed) {
    console.log('Profil unvollständig. Fehlende Felder:', response.lexware_missing_fields);
    
    // Zeige Formular für fehlende Daten
    const additionalData = await showProfileCompletionForm(response.lexware_missing_fields);
    
    // 4. Profil vervollständigen
    const completeResponse = await authClient.completeProfile({
      phone: additionalData.phone,
      street: additionalData.street,
      street_number: additionalData.streetNumber,
      city: additionalData.city,
      postal_code: additionalData.postalCode,
      country: additionalData.country
    });
    
    if (completeResponse.lexware_created) {
      showSuccess(`Profil vervollständigt! Deine Kundennummer: ${completeResponse.lexware_customer_number}`);
    }
  }
  
  // 5. Weiter zur App
  redirectToDashboard();
}

// Google Sign-In Button
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleGoogleLogin">
</div>
```

---

### Beispiel 3: Login mit MFA
```javascript
async function login(username, password) {
  try {
    // Versuch 1: Login ohne MFA-Token
    const response = await authClient.login({
      username,
      password
    });
    
    // MFA nicht erforderlich - Login erfolgreich
    if (!response.mfa_required) {
      tokenManager.setAccessToken(response.access);
      localStorage.setItem('refresh_token', response.refresh);
      redirectToDashboard();
      return;
    }
    
    // MFA erforderlich
    console.log('MFA erforderlich');
    
    // Zeige MFA-Eingabefeld
    const mfaToken = await showMFAPrompt();
    
    // Versuch 2: Login mit MFA-Token
    const mfaResponse = await authClient.login({
      username,
      password,
      mfa_token: mfaToken
    });
    
    // Login erfolgreich
    tokenManager.setAccessToken(mfaResponse.access);
    localStorage.setItem('refresh_token', mfaResponse.refresh);
    redirectToDashboard();
    
  } catch (error) {
    if (error.data?.mfa_required || error.data?.error === 'Invalid MFA token') {
      // MFA-Token war falsch
      showError('Ungültiger Code. Bitte versuche es erneut.');
      
      // Backup-Code-Option anzeigen
      showBackupCodeOption();
    } else if (error.status === 401) {
      showError('Falscher Benutzername oder Passwort');
    } else if (error.isRateLimited()) {
      showError('Zu viele Login-Versuche. Bitte warte kurz.');
    } else {
      showError('Ein Fehler ist aufgetreten');
    }
  }
}

// Mit Backup-Code anmelden
async function loginWithBackupCode(username, password) {
  const backupCode = await promptForBackupCode();
  
  const response = await authClient.login({
    username,
    password,
    mfa_token: backupCode // Backup-Codes funktionieren wie normale MFA-Tokens
  });
  
  // Warnung: Backup-Code wurde verwendet
  showWarning(`Backup-Code verwendet. Du hast noch ${response.backup_codes_remaining} Codes übrig.`);
  
  // Empfehle neue Backup-Codes zu generieren
  if (response.backup_codes_remaining < 3) {
    offerBackupCodeRegeneration();
  }
}
```

---

### Beispiel 4: SSO zwischen mehreren Websites
```javascript
// Website A: Benutzer meldet sich an
async function loginOnWebsiteA(username, password) {
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'WEBSITE_A_API_KEY'
    },
    body: JSON.stringify({ username, password }),
    credentials: 'include' // Wichtig: Session-Cookie setzen
  });
  
  const data = await response.json();
  
  // Token speichern
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
}

// Website B: Automatischer Login via SSO
async function checkSSOOnWebsiteB() {
  // 1. Prüfe SSO-Status
  const statusResponse = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/status/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'WEBSITE_B_API_KEY'
    },
    body: JSON.stringify({
      website_id: 'WEBSITE_B_ID'
    }),
    credentials: 'include' // Session-Cookie mitsenden
  });
  
  const statusData = await statusResponse.json();
  
  if (!statusData.sso_available) {
    // Kein SSO verfügbar - normaler Login erforderlich
    redirectToLogin();
    return;
  }
  
  // 2. SSO verfügbar - initiiere SSO
  const callbackUrl = `${window.location.origin}/auth/callback`;
  
  const ssoResponse = await fetch(
    `https://auth.palmdynamicx.de/api/accounts/sso/initiate/?website_id=WEBSITE_B_ID&return_url=${callbackUrl}`,
    {
      headers: { 'X-API-Key': 'WEBSITE_B_API_KEY' },
      credentials: 'include'
    }
  );
  
  const ssoData = await ssoResponse.json();
  
  // 3. Redirect zur Callback-URL mit SSO-Token
  window.location = ssoData.redirect_url;
}

// Website B: Callback-Handler
async function handleSSOCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const ssoToken = urlParams.get('sso_token');
  
  if (!ssoToken) {
    redirectToLogin();
    return;
  }
  
  // 4. SSO-Token gegen JWT-Tokens austauschen
  const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/exchange/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'WEBSITE_B_API_KEY'
    },
    body: JSON.stringify({
      token: ssoToken,
      website_id: 'WEBSITE_B_ID'
    })
  });
  
  const data = await response.json();
  
  // 5. Token speichern - User ist jetzt auf Website B angemeldet!
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  // 6. Redirect zu Dashboard
  window.location = '/dashboard';
}
```

---

### Beispiel 5: Passwort zurücksetzen mit E-Mail
```javascript
async function forgotPassword(email) {
  try {
    // 1. Passwort-Reset anfordern
    await authClient.requestPasswordReset({ email });
    
    showSuccess('Wir haben dir eine E-Mail mit einem Reset-Link gesendet.');
    
  } catch (error) {
    if (error.isRateLimited()) {
      showError('Zu viele Anfragen. Bitte warte 1 Stunde.');
    } else {
      showError('Ein Fehler ist aufgetreten');
    }
  }
}

// Benutzer klickt auf Link in E-Mail und kommt zu Reset-Page
async function handlePasswordReset() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  
  if (!token) {
    showError('Ungültiger oder fehlender Reset-Token');
    return;
  }
  
  // Zeige Formular für neues Passwort
  const newPassword = await showPasswordResetForm();
  
  try {
    // 2. Passwort zurücksetzen
    await authClient.resetPassword({
      token,
      new_password: newPassword,
      new_password2: newPassword
    });
    
    showSuccess('Passwort erfolgreich zurückgesetzt!');
    redirectToLogin();
    
  } catch (error) {
    if (error.status === 400 && error.data.token) {
      showError('Reset-Link ist abgelaufen oder ungültig. Bitte fordere einen neuen an.');
    } else {
      showError('Fehler beim Zurücksetzen des Passworts');
    }
  }
}
```

---

### Beispiel 6: Vollständiger Auth-Client
```javascript
class AuthAPIClient {
  constructor(apiKey, websiteId) {
    this.apiKey = apiKey;
    this.websiteId = websiteId;
    this.baseURL = 'https://auth.palmdynamicx.de';
    this.refreshPromise = null;
  }
  
  // === Authentifizierung ===
  
  async register(data) {
    return this.request('/api/accounts/register/', {
      method: 'POST',
      body: JSON.stringify({ ...data, website_id: this.websiteId })
    }, false);
  }
  
  async login(credentials) {
    return this.request('/api/accounts/login/', {
      method: 'POST',
      body: JSON.stringify(credentials)
    }, false);
  }
  
  async logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.request('/api/accounts/logout/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken })
    });
  }
  
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch(`${this.baseURL}/api/accounts/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (!response.ok) {
      this.clearAuth();
      throw new Error('Session expired');
    }
    
    const data = await response.json();
    tokenManager.setAccessToken(data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    return data;
  }
  
  // === MFA ===
  
  async enableMFA() {
    return this.request('/api/accounts/mfa/enable/', {
      method: 'POST',
      body: '{}'
    });
  }
  
  async verifyMFASetup(token) {
    return this.request('/api/accounts/mfa/verify-setup/', {
      method: 'POST',
      body: JSON.stringify({ token })
    });
  }
  
  async disableMFA(password, token) {
    return this.request('/api/accounts/mfa/disable/', {
      method: 'POST',
      body: JSON.stringify({ password, token })
    });
  }
  
  async getMFAStatus() {
    return this.request('/api/accounts/mfa/status/');
  }
  
  async regenerateBackupCodes(token) {
    return this.request('/api/accounts/mfa/backup-codes/', {
      method: 'POST',
      body: JSON.stringify({ token })
    });
  }
  
  // === Social Login ===
  
  async socialLogin(data) {
    return this.request('/api/accounts/social-login/', {
      method: 'POST',
      body: JSON.stringify(data)
    }, false);
  }
  
  async getSocialAccounts() {
    return this.request('/api/accounts/social-accounts/');
  }
  
  async unlinkSocialAccount(provider) {
    return this.request(`/api/accounts/social-accounts/${provider}/`, {
      method: 'DELETE'
    });
  }
  
  // === Profil ===
  
  async getProfile() {
    return this.request('/api/accounts/profile/');
  }
  
  async updateProfile(data) {
    return this.request('/api/accounts/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }
  
  async completeProfile(data) {
    return this.request('/api/accounts/complete-profile/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  async checkProfileCompletion(websiteId = null) {
    const body = websiteId ? { website_id: websiteId } : {};
    return this.request('/api/accounts/check-profile-completion/', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }
  
  async changePassword(oldPassword, newPassword) {
    return this.request('/api/accounts/change-password/', {
      method: 'POST',
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
        new_password2: newPassword
      })
    });
  }
  
  // === E-Mail ===
  
  async resendVerification(email) {
    return this.request('/api/accounts/resend-verification/', {
      method: 'POST',
      body: JSON.stringify({ email })
    }, false);
  }
  
  async verifyEmail(token) {
    return this.request('/api/accounts/verify-email/', {
      method: 'POST',
      body: JSON.stringify({ token })
    }, false);
  }
  
  async requestPasswordReset(email) {
    return this.request('/api/accounts/request-password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email })
    }, false);
  }
  
  async resetPassword(token, newPassword) {
    return this.request('/api/accounts/reset-password/', {
      method: 'POST',
      body: JSON.stringify({
        token,
        new_password: newPassword,
        new_password2: newPassword
      })
    }, false);
  }
  
  // === SSO ===
  
  async checkSSOStatus() {
    return this.request('/api/accounts/sso/status/', {
      method: 'POST',
      body: JSON.stringify({ website_id: this.websiteId })
    }, false, true); // credentials: include
  }
  
  async initiateSSO(returnUrl) {
    const url = `/api/accounts/sso/initiate/?website_id=${this.websiteId}&return_url=${returnUrl}`;
    return this.request(url, {}, false, true);
  }
  
  async exchangeSSOToken(token) {
    return this.request('/api/accounts/sso/exchange/', {
      method: 'POST',
      body: JSON.stringify({
        token,
        website_id: this.websiteId
      })
    }, false);
  }
  
  // === Hilfsmethoden ===
  
  async request(endpoint, options = {}, requiresAuth = true, includeCredentials = false) {
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
      ...options.headers
    };
    
    if (requiresAuth) {
      const accessToken = tokenManager.getAccessToken();
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
      }
    }
    
    const fetchOptions = {
      ...options,
      headers
    };
    
    if (includeCredentials) {
      fetchOptions.credentials = 'include';
    }
    
    let response = await fetch(`${this.baseURL}${endpoint}`, fetchOptions);
    
    // Token abgelaufen - versuche refresh
    if (response.status === 401 && requiresAuth) {
      if (!this.refreshPromise) {
        this.refreshPromise = this.refreshToken();
      }
      
      await this.refreshPromise;
      this.refreshPromise = null;
      
      // Wiederhole Request mit neuem Token
      headers['Authorization'] = `Bearer ${tokenManager.getAccessToken()}`;
      fetchOptions.headers = headers;
      response = await fetch(`${this.baseURL}${endpoint}`, fetchOptions);
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new AuthAPIError(response.status, data);
    }
    
    return data;
  }
  
  clearAuth() {
    tokenManager.clearTokens();
    localStorage.clear();
  }
}

// Verwendung
const authClient = new AuthAPIClient('pk_your_api_key', 'your-website-uuid');

// Registrieren
await authClient.register({
  email: 'user@example.com',
  username: 'user123',
  password: 'SecurePass123!',
  password2: 'SecurePass123!',
  first_name: 'Max',
  last_name: 'Mustermann'
});

// Login
const loginResponse = await authClient.login({
  username: 'user@example.com',
  password: 'SecurePass123!'
});

// Profil abrufen
const profile = await authClient.getProfile();
```

---

---

## 📊 Zusammenfassung aller Endpunkte

| Nr. | Endpunkt | Methode | Auth | Beschreibung |
|-----|----------|---------|------|--------------|
| 1 | `/api/accounts/register/` | POST | ❌ | Benutzer registrieren |
| 2 | `/api/accounts/login/` | POST | ❌ | Login (mit/ohne MFA) |
| 3 | `/api/accounts/token/refresh/` | POST | ❌ | Access Token erneuern |
| 4 | `/api/accounts/logout/` | POST | ✅ | Logout |
| 5 | `/api/accounts/resend-verification/` | POST | ✅ | Verifizierungs-E-Mail erneut senden |
| 6 | `/api/accounts/verify-email/` | POST | ❌ | E-Mail verifizieren |
| 7 | `/api/accounts/request-password-reset/` | POST | ❌ | Passwort-Reset anfordern |
| 8 | `/api/accounts/reset-password/` | POST | ❌ | Passwort zurücksetzen |
| 9 | `/api/accounts/change-password/` | POST | ✅ | Passwort ändern |
| 10 | `/api/accounts/profile/` | GET | ✅ | Profil abrufen |
| 11 | `/api/accounts/profile/` | PUT/PATCH | ✅ | Profil aktualisieren |
| 12 | `/api/accounts/social-login/` | POST | ❌ | Social Login |
| 13 | `/api/accounts/social-accounts/` | GET | ✅ | Social Accounts anzeigen |
| 14 | `/api/accounts/social-accounts/{provider}/` | DELETE | ✅ | Social Account entfernen |
| 15 | `/api/accounts/complete-profile/` | POST | ✅ | Profil vervollständigen |
| 16 | `/api/accounts/check-profile-completion/` | GET/POST | ✅ | Profil-Vollständigkeit prüfen |
| 17 | `/api/accounts/websites/` | GET | ✅ | Websites auflisten |
| 18 | `/api/accounts/websites/` | POST | ✅ | Website erstellen |
| 19 | `/api/accounts/websites/{id}/` | GET | ✅ | Website-Details abrufen |
| 20 | `/api/accounts/websites/{id}/required-fields/` | GET | ❌ | Website-Pflichtfelder abrufen |
| 21 | `/api/accounts/mfa/enable/` | POST | ✅ | MFA aktivieren |
| 22 | `/api/accounts/mfa/verify-setup/` | POST | ✅ | MFA-Setup verifizieren |
| 23 | `/api/accounts/mfa/disable/` | POST | ✅ | MFA deaktivieren |
| 24 | `/api/accounts/mfa/status/` | GET | ✅ | MFA-Status abrufen |
| 25 | `/api/accounts/mfa/verify/` | POST | ✅ | MFA-Token verifizieren |
| 26 | `/api/accounts/mfa/backup-codes/` | POST | ✅ | Backup-Codes neu generieren |
| 27 | `/api/accounts/sessions/` | GET | ✅ | Aktive Sessions anzeigen |
| 28 | `/api/accounts/sso/status/` | POST | ❌ | SSO Status prüfen |
| 29 | `/api/accounts/sso/initiate/` | GET | ❌ | SSO initiieren |
| 30 | `/api/accounts/sso/exchange/` | POST | ❌ | SSO-Token austauschen |
| 31 | `/api/accounts/sso/status/?token=` | GET | ❌ | SSO-Token Status prüfen |
| 32 | `/api/accounts/sso/logout/` | POST | 🍪 | SSO Logout |
| 33 | `/api/accounts/verify-access/` | POST | ✅ | Zugriff verifizieren |
| 34 | `/api/accounts/test-smtp/` | POST | ✅ Admin | SMTP testen |
| 35 | `/api/accounts/smtp-config/` | GET | ✅ Admin | SMTP-Konfiguration abrufen |

**Legende:**
- ✅ = Bearer Token erforderlich
- ❌ = Keine Authentifizierung erforderlich
- 🍪 = Session Cookie erforderlich
- Admin = Nur für Admin/Staff-Benutzer

**Hinweis:** ALLE Endpunkte erfordern einen gültigen API-Key im Header (`X-API-Key`)

---

## 🎓 Quick Start Guide

### 1. API-Key erhalten
1. Registriere eine Website im Admin-Panel: `https://auth.palmdynamicx.de/admin/`
2. Kopiere den generierten API-Key

### 2. Erste Registrierung
```javascript
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'SecurePass123!',
    password2: 'SecurePass123!',
    website_id: 'YOUR_WEBSITE_ID'
  })
});

const data = await response.json();
console.log('Access Token:', data.tokens.access);
```

### 3. Login
```javascript
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'SecurePass123!'
  })
});

const data = await response.json();

// Prüfe ob MFA erforderlich
if (data.mfa_required) {
  const mfaToken = prompt('MFA-Code:');
  // Erneut mit MFA-Token aufrufen
}
```

### 4. Profil abrufen
```javascript
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'X-API-Key': 'YOUR_API_KEY'
  }
});

const profile = await response.json();
console.log('User:', profile);
```

---

## 🆘 Support & Weitere Ressourcen

### Dokumentation
- 📖 **MFA-System**: [MFA_SYSTEM.md](./MFA_SYSTEM.md)
- 📖 **SSO-System**: [SSO_SYSTEM.md](./SSO_SYSTEM.md)
- 📖 **Social Login**: [SOCIAL_LOGIN.md](./SOCIAL_LOGIN.md)
- 📖 **Lexware-Integration**: [LEXWARE_INTEGRATION.md](./LEXWARE_INTEGRATION.md)
- 📖 **E-Mail-System**: [EMAIL_SYSTEM.md](./EMAIL_SYSTEM.md)
- 📖 **Berechtigungen**: [PERMISSIONS_GUIDE.md](./PERMISSIONS_GUIDE.md)
- 📖 **API-Key-Authentifizierung**: [API_KEY_AUTHENTICATION.md](./API_KEY_AUTHENTICATION.md)

### Postman Collection
Eine vollständige Postman Collection mit allen Endpunkten findest du hier:
- `Auth-Service-API-Complete.postman_collection.json`

### Support
- 📧 E-Mail: support@palmdynamicx.de
- 🌐 Website: https://palmdynamicx.de
- 📝 GitHub Issues: [Repository-Link]

### Changelog
**Version 2.0 (Januar 2026)**
- ✅ Vollständige MFA-Integration mit Login-Flow
- ✅ Erweiterte SSO-Funktionalität
- ✅ Social Login für 5+ Provider
- ✅ Automatische Lexware-Integration
- ✅ Umfassende Fehlerbehandlung
- ✅ API-Key-Authentifizierung für alle Endpunkte
- ✅ Rate Limiting & Security-Verbesserungen

**Version 1.0 (Dezember 2025)**
- ✅ Basis-Authentifizierung
- ✅ E-Mail Verifizierung
- ✅ Passwort-Reset
- ✅ JWT-Token Management

---

**Ende der Dokumentation** | Stand: Januar 2026 | Version 2.0
