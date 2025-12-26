# 🔐 Auth Service - Vollständige API Dokumentation

**Base URL**: `https://auth.palmdynamicx.de`  
**Version**: 1.0  
**Authentifizierung**: JWT Bearer Tokens

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

## 🎭 Multi-Factor Authentication (MFA)

### 21. MFA aktivieren
```
POST /api/accounts/mfa/enable/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
{
  "qr_code": "data:image/png;base64,...",
  "secret": "JBSWY3DPEHPK3PXP",
  "message": "Scanne den QR-Code mit deiner Authenticator-App"
}
```

---

### 22. MFA-Setup verifizieren
```
POST /api/accounts/mfa/verify-setup/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "backup_codes": [
    "ABC123DEF456",
    "GHI789JKL012",
    "MNO345PQR678"
  ],
  "message": "MFA erfolgreich aktiviert."
}
```

---

### 23. MFA deaktivieren
```
POST /api/accounts/mfa/disable/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "MFA erfolgreich deaktiviert."
}
```

---

### 24. MFA-Status abrufen
```
GET /api/accounts/mfa/status/
```

**Authentifizierung**: Bearer Token erforderlich

**Response** (200 OK):
```json
{
  "mfa_enabled": true,
  "backup_codes_count": 3
}
```

---

### 25. MFA-Token verifizieren (beim Login)
```
POST /api/accounts/mfa/verify/
```

**Authentifizierung**: Keine (wird nach erfolgreichem Login aufgerufen)

**Request Body**:
```json
{
  "user_id": "uuid",
  "token": "123456"
}
```

**Response** (200 OK):
```json
{
  "valid": true,
  "message": "MFA-Token ist gültig."
}
```

---

## 📊 Sessions

### 26. Aktive Sessions anzeigen
```
GET /api/accounts/sessions/
```

**Authentifizierung**: Bearer Token erforderlich

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

### 27. SSO initiieren
```
POST /api/accounts/sso/initiate/
```

**Authentifizierung**: Bearer Token erforderlich

**Request Body**:
```json
{
  "website_id": "uuid",
  "redirect_uri": "https://example.com/auth/callback"
}
```

**Response** (200 OK):
```json
{
  "sso_url": "https://auth.example.com/sso/callback/?token=xxx",
  "token": "sso-token-xxx",
  "expires_in": 300
}
```

---

### 28. SSO-Token austauschen
```
POST /api/accounts/sso/exchange/
```

**Authentifizierung**: Keine

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
  "user": { ... }
}
```

---

### 29. SSO-Status prüfen
```
GET /api/accounts/sso/status/?token=xxx
```

**Authentifizierung**: Keine

**Response** (200 OK):
```json
{
  "valid": true,
  "user_id": "uuid",
  "website_id": "uuid",
  "expires_at": "2025-12-26T10:05:00Z"
}
```

---

## 🔍 Zugriffsprüfung

### 30. Zugriff verifizieren
```
POST /api/accounts/verify-access/
```

**Authentifizierung**: Bearer Token erforderlich

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
  "user": { ... },
  "website": {
    "id": "uuid",
    "name": "Meine Website",
    "domain": "example.com"
  }
}
```

---

## 📱 SMTP Konfiguration

### 31. SMTP testen
```
POST /api/accounts/test-smtp/
```

**Authentifizierung**: Bearer Token erforderlich (Admin/Staff)

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
  "message": "Test-E-Mail erfolgreich gesendet."
}
```

---

### 32. SMTP-Konfiguration abrufen
```
GET /api/accounts/smtp-config/
```

**Authentifizierung**: Bearer Token erforderlich (Admin/Staff)

**Response** (200 OK):
```json
{
  "email_host": "smtp.zoho.eu",
  "email_port": 465,
  "email_use_ssl": true,
  "email_from": "noreply@example.com"
}
```

---

## ⚠️ Fehlerbehandlung

Alle Endpoints können folgende Fehler zurückgeben:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "email": ["Dieses Feld ist erforderlich."],
    "password": ["Passwort muss mindestens 8 Zeichen lang sein."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Ein unerwarteter Fehler ist aufgetreten."
}
```

---

## 🔑 Authentifizierung

### JWT Bearer Token
Die meisten Endpoints benötigen einen Bearer Token im Authorization Header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Token-Lebensdauer
- **Access Token**: 1 Stunde
- **Refresh Token**: 7 Tage

### Token erneuern
Wenn der Access Token abläuft, verwende den Refresh Token um einen neuen zu erhalten:

```
POST /api/accounts/token/refresh/
Body: { "refresh": "eyJ0eXAi..." }
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

Fehlende Felder werden in der Response angezeigt.

### Rate Limiting
- Standard: 100 Requests pro Minute pro IP
- Login: 5 Versuche pro 15 Minuten
- Passwort-Reset: 3 Anfragen pro Stunde

### CORS
Alle registrierten Origins in `allowed_origins` sind erlaubt.

### Pagination
Listen-Endpoints unterstützen Pagination:
- `?page=2` - Seite 2
- `?page_size=50` - 50 Einträge pro Seite

---

## 📚 Verwendungsbeispiele

### Beispiel 1: Kompletter Registrierungs-Flow
```javascript
// 1. Registrieren
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'SecurePass123!',
    password2: 'SecurePass123!',
    first_name: 'Max',
    last_name: 'Mustermann',
    website_id: 'website-uuid'
  })
});

const data = await response.json();
const accessToken = data.tokens.access;

// 2. Profil abrufen
const profile = await fetch('https://auth.palmdynamicx.de/api/accounts/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

### Beispiel 2: Social Login mit Profil-Vervollständigung
```javascript
// 1. Google Login
const socialLogin = await fetch('https://auth.palmdynamicx.de/api/accounts/social-login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    provider: 'google',
    provider_user_id: '1234567890',
    email: 'user@gmail.com',
    first_name: 'Max',
    last_name: 'Mustermann'
  })
});

const loginData = await socialLogin.json();

// 2. Prüfe ob Profil vollständig
if (!loginData.lexware_ready) {
  // 3. Profil vervollständigen
  const complete = await fetch('https://auth.palmdynamicx.de/api/accounts/complete-profile/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${loginData.tokens.access}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      street: 'Musterstraße',
      street_number: '123',
      city: 'Berlin',
      postal_code: '10115',
      country: 'Deutschland'
    })
  });
  
  const completeData = await complete.json();
  console.log('Lexware Kundennummer:', completeData.lexware_customer_number);
}
```

---

**Ende der Dokumentation**
