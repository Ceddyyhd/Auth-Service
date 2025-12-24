# 📚 API-Referenz - Auth Service

Vollständige API-Dokumentation für den zentralen Authentication Service.

## � Wichtiger Sicherheitshinweis

**ALLE API-Anfragen MÜSSEN über HTTPS erfolgen!**

- ✅ In Produktion: Nur HTTPS verwenden (`https://api.ihredomain.com`)
- ⚠️ In Entwicklung: HTTP erlaubt (`http://localhost:8000`)
- 🔐 JWT-Tokens werden verschlüsselt übertragen
- 🛡️ Passwörter werden mit bcrypt gehasht (NIEMALS im Klartext gespeichert)
- 📡 Sensible Daten werden nur verschlüsselt übertragen
- 🔑 API-Keys und Tokens niemals im Client-Code hardcoden
- 🌐 CORS ist aktiviert - nur registrierte Origins erlaubt

### Sicherheits-Checkliste für Produktion:

```python
# settings.py - Produktions-Einstellungen
DEBUG = False
SECURE_SSL_REDIRECT = True          # Erzwinge HTTPS
SESSION_COOKIE_SECURE = True        # Cookies nur über HTTPS
CSRF_COOKIE_SECURE = True           # CSRF nur über HTTPS
SECURE_HSTS_SECONDS = 31536000      # HTTP Strict Transport Security
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## 📋 Inhaltsverzeichnis

- [🔒 Sicherheitshinweise](#wichtiger-sicherheitshinweis)
- [🔐 Authentifizierung](#authentifizierung)
- [👤 Benutzer-Verwaltung](#benutzer-verwaltung)
- [🌐 Website-Verwaltung](#website-verwaltung)
- [🔑 Permissions & Rollen](#permissions--rollen)
- [🔗 Social Login](#social-login)
- [📊 Sessions](#sessions)
- [⚠️ Fehlerbehandlung](#fehlerbehandlung)

## 📝 Allgemeine Request-Struktur

Alle API-Anfragen folgen diesem Format:

```http
POST /api/endpoint/ HTTP/1.1
Host: api.ihredomain.com
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>

{
  "field": "value"
}
```

---

## 🔐 Authentifizierung

### 1. Registrierung

Erstellt einen neuen Benutzer-Account. Passwort wird automatisch mit bcrypt gehasht.

**📍 Endpoint:** `POST /api/accounts/register/`  
**🔓 Berechtigung:** Keine (öffentlich)  
**🔒 Verschlüsselung:** HTTPS erforderlich (Produktion)

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `email` | string | ✅ Ja | Body | E-Mail-Adresse (einzigartig) |
| `username` | string | ✅ Ja | Body | Benutzername (einzigartig) |
| `password` | string | ✅ Ja | Body | Min. 8 Zeichen, Sonderzeichen empfohlen |
| `password_confirm` | string | ✅ Ja | Body | Muss mit `password` übereinstimmen |
| `first_name` | string | ⚠️ * | Body | Vorname |
| `last_name` | string | ⚠️ * | Body | Nachname |
| `website_id` | UUID | ✅ Ja | Body | ID der registrierenden Website |
| `phone` | string | ⚠️ * | Body | Telefonnummer (Format: +49...) |
| `street` | string | ⚠️ * | Body | Straße |
| `street_number` | string | ⚠️ * | Body | Hausnummer |
| `city` | string | ⚠️ * | Body | Stadt |
| `postal_code` | string | ⚠️ * | Body | Postleitzahl |
| `country` | string | ⚠️ * | Body | Land |
| `date_of_birth` | date | ⚠️ * | Body | Geburtsdatum (YYYY-MM-DD) |
| `company` | string | ⚠️ * | Body | Firmenname |

*⚠️ Abhängig von den Website-Einstellungen (require_first_name, require_phone, etc.)*

#### ✅ Erfolgreiche Response (201 Created):

```json
{
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "email": "max.mustermann@example.com",
    "username": "maxmuster",
    "first_name": "Max",
    "last_name": "Mustermann",
    "phone": "+491234567890",
    "city": "Berlin",
    "postal_code": "10115",
    "profile_completed": true,
    "is_verified": false,
    "is_active": true,
    "date_joined": "2025-12-24T10:30:45.123456Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Benutzer erfolgreich registriert. Bitte verifizieren Sie Ihre E-Mail."
}
```

#### ❌ Fehler-Response (400 Bad Request):

```json
{
  "error": "Validation error",
  "details": {
    "email": ["Benutzer mit dieser E-Mail existiert bereits."],
    "password": ["Passwort muss mindestens 8 Zeichen lang sein."],
    "password_confirm": ["Passwörter stimmen nicht überein."],
    "phone": ["Ungültiges Telefonnummern-Format."]
  }
}
```

#### 🔒 Sicherheitshinweise:

- ✅ Passwort wird **niemals** im Klartext gespeichert (bcrypt Hash)
- ✅ E-Mail und Username müssen einzigartig sein
- ✅ JWT-Tokens sind signiert und haben Ablaufzeit
- ✅ Verifizierungs-E-Mail wird automatisch gesendet
- ⚠️ **NIEMALS** Tokens in URL-Parametern übergeben
- ⚠️ Tokens nur in Authorization-Header oder httpOnly-Cookies speichern

#### 💻 Frontend-Beispiel (Secure):

```javascript
/**
 * Sicherer Registrierungs-Flow mit Verschlüsselung
 */
async function secureRegister(userData) {
  try {
    // 🔒 HTTPS Endpoint verwenden in Produktion
    const API_URL = process.env.NODE_ENV === 'production' 
      ? 'https://auth.palmdynamicx.de'
      : 'http://localhost:8000';
    
    const response = await fetch(`${API_URL}/api/accounts/register/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
        // Kein Authorization-Header bei Registrierung
      },
      body: JSON.stringify({
        email: userData.email,
        username: userData.username,
        password: userData.password,  // Wird serverseitig gehasht
        password_confirm: userData.passwordConfirm,
        first_name: userData.firstName,
        last_name: userData.lastName,
        website_id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
        phone: userData.phone || null,
        city: userData.city || null,
        postal_code: userData.postalCode || null
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      // Fehlerbehandlung
      throw new Error(data.error || 'Registrierung fehlgeschlagen');
    }
    
    // 🔒 Tokens sicher speichern
    // Option 1: localStorage (Einfach, aber weniger sicher)
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    
    // Option 2: httpOnly Cookie (Sicherer) - Backend muss Cookie setzen
    // Tokens werden automatisch bei jedem Request mitgesendet
    
    // ✅ Erfolg
    return {
      success: true,
      user: data.user,
      message: data.message
    };
    
  } catch (error) {
    console.error('❌ Registrierung fehlgeschlagen:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Verwendung:
const result = await secureRegister({
  email: 'max@example.com',
  username: 'maxmuster',
  password: 'Sicher3sP@ssw0rt!',
  passwordConfirm: 'Sicher3sP@ssw0rt!',
  firstName: 'Max',
  lastName: 'Mustermann',
  phone: '+491234567890'
});

if (result.success) {
  console.log('✅ Registrierung erfolgreich:', result.user);
  // Weiterleitung zur Verifizierungs-Seite
  window.location.href = '/email-verification';
} else {
  console.error('❌ Fehler:', result.error);
}
```

---

### 2. Login

Authentifiziert einen Benutzer und gibt JWT-Tokens zurück.

**📍 Endpoint:** `POST /api/accounts/login/`  
**🔓 Berechtigung:** Keine (öffentlich)  
**🔒 Verschlüsselung:** HTTPS erforderlich (Produktion)

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `username` | string | ✅ Ja | Body | E-Mail ODER Username |
| `password` | string | ✅ Ja | Body | Passwort (wird serverseitig validiert) |

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwODg3MjAwMCwidXNlcl9pZCI6ImY0N2FjMTBiLTU4Y2MtNDM3Mi1hNTY3LTBlMDJiMmMzZDQ3OSJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4Nzg1NjAwLCJ1c2VyX2lkIjoiZjQ3YWMxMGItNThjYy00MzcyLWE1NjctMGUwMmIyYzNkNDc5In0...",
  "user": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "email": "max.mustermann@example.com",
    "username": "maxmuster",
    "first_name": "Max",
    "last_name": "Mustermann",
    "is_verified": true
  }
}
```

**JWT Token Struktur (Decoded):**
```json
// Access Token (Gültig 15 Minuten)
{
  "token_type": "access",
  "exp": 1708785600,
  "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "username": "maxmuster",
  "email": "max@example.com"
}

// Refresh Token (Gültig 7 Tage)
{
  "token_type": "refresh",
  "exp": 1708872000,
  "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

#### ❌ Fehler-Response (401 Unauthorized):

```json
{
  "detail": "Ungültige Anmeldedaten.",
  "error_code": "invalid_credentials"
}
```

#### 🔒 Sicherheitshinweise:

- ✅ Passwort wird **nie** im Klartext gespeichert oder zurückgegeben
- ✅ Access Token läuft nach 15 Minuten ab
- ✅ Refresh Token läuft nach 7 Tagen ab
- ✅ Tokens sind signiert und können nicht gefälscht werden
- ⚠️ **NIEMALS** Tokens in Logs ausgeben
- ⚠️ Bei mehrfachen fehlgeschlagenen Login-Versuchen: Rate Limiting aktiv
- 🔐 IP-Adresse und User-Agent werden für Session-Tracking gespeichert

#### 💻 Frontend-Beispiel (Secure):

```javascript
/**
 * Sicherer Login mit automatischem Token-Management
 */
class SecureAuthService {
  static API_URL = process.env.NODE_ENV === 'production'
    ? 'https://auth.palmdynamicx.de'
    : 'http://localhost:8000';
  
  /**
   * Login-Funktion mit Fehlerbehandlung
   */
  static async login(email, password) {
    try {
      const response = await fetch(`${this.API_URL}/api/accounts/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // KEIN Authorization-Header beim Login
        },
        body: JSON.stringify({
          username: email,  // Kann E-Mail oder Username sein
          password: password
        }),
        credentials: 'include'  // Für httpOnly Cookies
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Login fehlgeschlagen');
      }
      
      // 🔒 Tokens sicher speichern
      this.setTokens(data.access, data.refresh);
      
      // ✅ User-Daten zurückgeben (OHNE Passwort!)
      return {
        success: true,
        user: data.user,
        tokens: {
          access: data.access,
          refresh: data.refresh
        }
      };
      
    } catch (error) {
      console.error('❌ Login fehlgeschlagen:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Tokens sicher speichern
   */
  static setTokens(accessToken, refreshToken) {
    // Option 1: localStorage (einfach, aber XSS-anfällig)
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    
    // Option 2: sessionStorage (sicherer, nur für aktuelle Session)
    // sessionStorage.setItem('access_token', accessToken);
    
    // ⚠️ NIEMALS in Cookies ohne httpOnly-Flag speichern!
  }
  
  /**
   * Token aus Storage holen
   */
  static getAccessToken() {
    return localStorage.getItem('access_token');
  }
  
  static getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }
  
  /**
   * Prüft ob Benutzer eingeloggt ist
   */
  static isAuthenticated() {
    const token = this.getAccessToken();
    if (!token) return false;
    
    try {
      // Token decodieren (nur Payload, Signatur serverseitig prüfen!)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = payload.exp * 1000;
      
      // Prüfen ob abgelaufen
      return Date.now() < expirationTime;
    } catch {
      return false;
    }
  }
  
  /**
   * Authentifizierten API-Request durchführen
   */
  static async authenticatedFetch(endpoint, options = {}) {
    const token = this.getAccessToken();
    
    if (!token) {
      throw new Error('Nicht authentifiziert');
    }
    
    // 🔒 Authorization Header hinzufügen
    const response = await fetch(`${this.API_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // ✅ Token im Header
      }
    });
    
    // Auto-Refresh bei 401
    if (response.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        // Retry mit neuem Token
        return this.authenticatedFetch(endpoint, options);
      } else {
        // Logout bei fehlgeschlagenem Refresh
        this.logout();
        throw new Error('Session abgelaufen');
      }
    }
    
    return response;
  }
  
  /**
   * Access Token erneuern
   */
  static async refreshToken() {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) return false;
    
    try {
      const response = await fetch(`${this.API_URL}/api/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });
      
      if (!response.ok) return false;
      
      const data = await response.json();
      this.setTokens(data.access, refreshToken);
      
      return true;
    } catch {
      return false;
    }
  }
  
  /**
   * Logout (Tokens löschen)
   */
  static logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
}

// ✅ VERWENDUNG:
async function handleLogin() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  const result = await SecureAuthService.login(email, password);
  
  if (result.success) {
    console.log('✅ Login erfolgreich:', result.user);
    // Weiterleitung zum Dashboard
    window.location.href = '/dashboard';
  } else {
    console.error('❌ Login fehlgeschlagen:', result.error);
    alert(result.error);
  }
}

// Geschützten Endpoint aufrufen:
const response = await SecureAuthService.authenticatedFetch('/api/accounts/profile/');
const userData = await response.json();
```

---

### 3. Logout

Meldet den Benutzer ab und invalidiert den Refresh-Token.

**📍 Endpoint:** `POST /api/accounts/logout/`  
**🔒 Berechtigung:** IsAuthenticated  
**🔑 Header:** `Authorization: Bearer <ACCESS_TOKEN>`

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `refresh` | string (JWT) | ✅ Ja | Body | Refresh Token zum Invalidieren |

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "message": "Erfolgreich abgemeldet.",
  "detail": "Refresh token wurde invalidiert."
}
```

#### 💻 Frontend-Beispiel:

```javascript
async function secureLogout() {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    const accessToken = localStorage.getItem('access_token');
    
    // Refresh-Token serverseitig invalidieren
    await fetch('https://api.ihredomain.com/api/accounts/logout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`  // ✅ Access Token im Header
      },
      body: JSON.stringify({
        refresh: refreshToken  // ✅ Refresh Token im Body
      })
    });
    
    // ✅ Tokens lokal löschen
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.clear();
    
    // ✅ Weiterleitung
    window.location.href = '/login';
    
  } catch (error) {
    console.error('Logout-Fehler:', error);
    // Auch bei Fehler Tokens löschen
    localStorage.clear();
    window.location.href = '/login';
  }
}
```

---

### 4. Token Refresh

Erneuert einen abgelaufenen Access-Token mit einem gültigen Refresh-Token.

**📍 Endpoint:** `POST /api/token/refresh/`  
**🔓 Berechtigung:** Keine  
**🔒 Verschlüsselung:** HTTPS erforderlich

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `refresh` | string (JWT) | ✅ Ja | Body | Gültiger Refresh Token |

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4Nzg2NTAwLCJ1c2VyX2lkIjoiZjQ3YWMxMGItNThjYy00MzcyLWE1NjctMGUwMmIyYzNkNDc5In0..."
}
```

#### ❌ Fehler-Response (401 Unauthorized):

```json
{
  "detail": "Token ist ungültig oder abgelaufen",
  "code": "token_not_valid"
}
```

#### 🔒 Sicherheitshinweise:

- ✅ Refresh Token wird **nicht** erneuert (bleibt gleich)
- ✅ Neuer Access Token ist 15 Minuten gültig
- ⚠️ Nach 7 Tagen muss Benutzer sich neu einloggen
- ⚠️ Bei gestohlenen Refresh-Tokens: Sofort alle Sessions invalidieren

#### 💻 Frontend-Beispiel (Axios Interceptor):

```javascript
import axios from 'axios';

// API-Client mit Auto-Refresh
const apiClient = axios.create({
  baseURL: 'https://api.ihredomain.com',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request-Interceptor: Token hinzufügen
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response-Interceptor: Auto-Refresh bei 401
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Wenn 401 und noch nicht versucht zu refreshen
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        // Token erneuern
        const response = await axios.post(
          'https://api.ihredomain.com/api/token/refresh/',
          { refresh: refreshToken }
        );
        
        const newAccessToken = response.data.access;
        
        // Neuen Token speichern
        localStorage.setItem('access_token', newAccessToken);
        
        // Original-Request mit neuem Token wiederholen
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
        
      } catch (refreshError) {
        // Refresh fehlgeschlagen - Logout
        console.error('❌ Token-Refresh fehlgeschlagen:', refreshError);
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// ✅ VERWENDUNG:
// Alle Requests nutzen automatisch Token-Refresh
try {
  const response = await apiClient.get('/api/accounts/profile/');
  console.log('Profil:', response.data);
} catch (error) {
  console.error('Fehler:', error);
}
```

---

### 5. Passwort zurücksetzen (Anfrage)

Sendet eine E-Mail mit einem Passwort-Reset-Link.

**📍 Endpoint:** `POST /api/accounts/password-reset/`  
**🔓 Berechtigung:** Keine (öffentlich)

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `email` | string | ✅ Ja | Body | E-Mail-Adresse des Accounts |

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "message": "Falls ein Account mit dieser E-Mail existiert, wurde ein Reset-Link gesendet.",
  "email_sent": true
}
```

**Hinweis:** Aus Sicherheitsgründen wird immer die gleiche Nachricht zurückgegeben, unabhängig davon ob der Account existiert.

#### 🔒 Sicherheitshinweise:

- ✅ Rate Limiting: Max 3 Anfragen pro Stunde pro IP
- ✅ Token läuft nach 1 Stunde ab
- ✅ Token kann nur einmal verwendet werden
- ⚠️ Gibt nicht preis ob E-Mail existiert (Security by Obscurity)

#### E-Mail-Inhalt:

```
Betreff: Passwort zurücksetzen

Hallo,

Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt.

Klicken Sie auf den folgenden Link (gültig für 1 Stunde):
https://ihredomain.com/reset-password?token=abc123...

Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail.

Viele Grüße
Ihr Auth-Service Team
```

---

### 6. Passwort zurücksetzen (Bestätigung)

Setzt ein neues Passwort mit einem gültigen Reset-Token.

**📍 Endpoint:** `POST /api/accounts/password-reset-confirm/`  
**🔓 Berechtigung:** Keine (öffentlich)

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `token` | string | ✅ Ja | Body | Reset-Token aus E-Mail |
| `password` | string | ✅ Ja | Body | Neues Passwort (min. 8 Zeichen) |
| `password_confirm` | string | ✅ Ja | Body | Passwort-Bestätigung |

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "message": "Passwort erfolgreich geändert. Sie können sich jetzt anmelden.",
  "password_changed": true
}
```

#### ❌ Fehler-Response (400 Bad Request):

```json
{
  "error": "Token ist ungültig oder abgelaufen",
  "token_valid": false
}
```

---

## 👤 Benutzer-Verwaltung

### 7. Profil abrufen

Gibt das komplette Benutzerprofil zurück (ohne Passwort!).

**📍 Endpoint:** `GET /api/accounts/profile/`  
**🔒 Berechtigung:** IsAuthenticated  
**🔑 Header:** `Authorization: Bearer <ACCESS_TOKEN>`

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "max.mustermann@example.com",
  "username": "maxmuster",
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+491234567890",
  "street": "Musterstraße",
  "street_number": "42",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "date_of_birth": "1990-01-15",
  "company": "Meine Firma GmbH",
  "profile_completed": true,
  "is_verified": true,
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2025-01-01T10:00:00.000000Z",
  "last_login": "2025-12-24T08:30:15.123456Z",
  "roles": [
    {
      "id": "role-uuid",
      "name": "Editor",
      "scope": "local",
      "website": "Meine Website"
    }
  ],
  "permissions_count": 12
}
```

**Hinweis:** Passwort wird **NIEMALS** zurückgegeben!

#### 💻 Frontend-Beispiel:

```javascript
async function loadUserProfile() {
  try {
    const response = await SecureAuthService.authenticatedFetch('/api/accounts/profile/');
    const user = await response.json();
    
    // Profil anzeigen
    document.getElementById('userName').textContent = user.first_name + ' ' + user.last_name;
    document.getElementById('userEmail').textContent = user.email;
    
    // Verifizierungs-Status prüfen
    if (!user.is_verified) {
      showEmailVerificationBanner();
    }
    
    return user;
  } catch (error) {
    console.error('Profil laden fehlgeschlagen:', error);
  }
}
```

---

### 8. Profil aktualisieren

Aktualisiert Benutzer-Profilfelder (Passwort ausgenommen).

**📍 Endpoint:** `PATCH /api/accounts/profile/`  
**🔒 Berechtigung:** IsAuthenticated  
**🔑 Header:** `Authorization: Bearer <ACCESS_TOKEN>`

#### Request Body (application/json):

| Feld | Typ | Pflicht | Wo eintragen | Beschreibung |
|------|-----|---------|--------------|--------------|
| `first_name` | string | ❌ Nein | Body | Vorname |
| `last_name` | string | ❌ Nein | Body | Nachname |
| `phone` | string | ❌ Nein | Body | Telefonnummer |
| `city` | string | ❌ Nein | Body | Stadt |
| ... | ... | ❌ Nein | Body | Beliebige Profilfelder |

**Hinweis:** Nur gesendete Felder werden aktualisiert (PATCH-Semantik).

#### ✅ Erfolgreiche Response (200 OK):

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "first_name": "Maximilian",
  "phone": "+491234567890",
  "city": "München",
  "updated_at": "2025-12-24T10:45:30.123456Z"
}
```

#### ❌ Fehler-Response (400 Bad Request):

```json
{
  "error": "Validation error",
  "details": {
    "phone": ["Ungültiges Telefonnummern-Format."]
  }
}
```

#### 🔒 Sicherheitshinweise:

- ⚠️ **Passwort kann NICHT über diesen Endpoint geändert werden**
- ⚠️ E-Mail-Änderung erfordert Verifizierung
- ⚠️ Username kann nach Erstellung nicht geändert werden

#### 💻 Frontend-Beispiel:

```javascript
async function updateProfile(updates) {
  try {
    const response = await SecureAuthService.authenticatedFetch(
      '/api/accounts/profile/',
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      }
    );
    
    const updatedUser = await response.json();
    console.log('✅ Profil aktualisiert:', updatedUser);
    return updatedUser;
    
  } catch (error) {
    console.error('❌ Update fehlgeschlagen:', error);
    throw error;
  }
}

// Verwendung:
await updateProfile({
  first_name: 'Maximilian',
  city: 'München',
  phone: '+498912345678'
});
```

---

### E-Mail verifizieren

**Endpoint:** `POST /api/accounts/verify-email/`  
**Berechtigung:** Keine (öffentlich)

```javascript
// Request
{
  "token": "verification-token-hier"
}

// Response (200 OK)
{
  "message": "E-Mail erfolgreich verifiziert.",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_verified": true
  }
}
```

**Frontend Beispiel:**
```javascript
// Token aus URL extrahieren
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

if (token) {
  await fetch('http://localhost:8000/api/accounts/verify-email/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  });
}
```

---

### Profil vervollständigen (nach Social Login)

**Endpoint:** `POST /api/accounts/complete-profile/`  
**Berechtigung:** IsAuthenticated

```javascript
// Request
{
  "website_id": "website-uuid",
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789"
}

// Response (200 OK)
{
  "message": "Profil erfolgreich vervollständigt.",
  "user": {
    "id": "uuid",
    "profile_completed": true
  }
}
```

---

### Profil-Vollständigkeit prüfen

**Endpoint:** `GET /api/accounts/check-profile/{website_id}/`  
**Berechtigung:** IsAuthenticated

```javascript
// Response (200 OK - Fehlende Felder)
{
  "completed": false,
  "missing_fields": ["first_name", "last_name", "phone"],
  "required_fields": {
    "first_name": true,
    "last_name": true,
    "phone": true,
    "address": false
  }
}
```

---

## 🌐 Website-Verwaltung

### Alle Websites auflisten

**Endpoint:** `GET /api/accounts/websites/`  
**Berechtigung:** IsAdminUser

```javascript
// Response (200 OK)
[
  {
    "id": "uuid",
    "name": "Meine Website",
    "domain": "example.com",
    "callback_url": "https://example.com/auth/callback",
    "allowed_origins": ["https://example.com"],
    "is_active": true,
    "require_email_verification": true,
    "require_first_name": true,
    "require_last_name": true,
    "require_phone": false,
    "require_address": false,
    "created_at": "2025-01-01T10:00:00Z"
  }
]
```

---

### Website erstellen

**Endpoint:** `POST /api/accounts/websites/`  
**Berechtigung:** IsAdminUser

```javascript
// Request
{
  "name": "Neue Website",
  "domain": "newsite.com",
  "callback_url": "https://newsite.com/auth/callback",
  "allowed_origins": ["https://newsite.com"],
  "require_first_name": true,
  "require_last_name": true
}
```

---

### Website aktualisieren

**Endpoint:** `PATCH /api/accounts/websites/{id}/`  
**Berechtigung:** IsAdminUser

```javascript
// Request
{
  "is_active": false,
  "require_phone": true
}
```

---

## 🔑 Permissions & Rollen

### Alle Permissions auflisten

**Endpoint:** `GET /api/permissions/`  
**Berechtigung:** IsAuthenticated  
**Query Parameters:** `?website=<uuid>&scope=global|local`

```javascript
// Response (200 OK)
[
  {
    "id": "uuid",
    "code": "users.view",
    "name": "Benutzer anzeigen",
    "description": "Erlaubt das Ansehen von Benutzerdaten",
    "scope": "global",
    "website": null
  },
  {
    "id": "uuid",
    "code": "posts.edit",
    "name": "Beiträge bearbeiten",
    "description": "Erlaubt das Bearbeiten von Beiträgen",
    "scope": "local",
    "website": {
      "id": "uuid",
      "name": "Blog Website"
    }
  }
]
```

**Frontend Beispiel:**
```javascript
// Alle globalen Permissions
const globalPerms = await fetch('/api/permissions/?scope=global');

// Permissions für spezifische Website
const websitePerms = await fetch('/api/permissions/?website=<uuid>');
```

---

### Permission erstellen

**Endpoint:** `POST /api/permissions/`  
**Berechtigung:** IsAdminUser

```javascript
// Globale Permission
{
  "code": "users.delete",
  "name": "Benutzer löschen",
  "description": "Erlaubt das Löschen von Benutzern",
  "scope": "global",
  "website": null
}

// Lokale Permission
{
  "code": "products.edit",
  "name": "Produkte bearbeiten",
  "description": "Erlaubt das Bearbeiten von Produkten",
  "scope": "local",
  "website": "website-uuid"
}
```

---

### Alle Rollen auflisten

**Endpoint:** `GET /api/roles/`  
**Berechtigung:** IsAuthenticated  
**Query Parameters:** `?website=<uuid>&scope=global|local`

```javascript
// Response (200 OK)
[
  {
    "id": "uuid",
    "name": "Administrator",
    "description": "Vollständiger System-Zugriff",
    "scope": "global",
    "website": null,
    "permissions": [
      {
        "id": "uuid",
        "code": "users.view",
        "name": "Benutzer anzeigen"
      },
      {
        "id": "uuid",
        "code": "users.edit",
        "name": "Benutzer bearbeiten"
      }
    ]
  }
]
```

---

### Rolle erstellen

**Endpoint:** `POST /api/roles/`  
**Berechtigung:** IsAdminUser

```javascript
// Globale Rolle mit mehreren Permissions
{
  "name": "Content Manager",
  "description": "Verwaltet Inhalte auf allen Websites",
  "scope": "global",
  "website": null,
  "permissions": [
    "permission-uuid-1",
    "permission-uuid-2",
    "permission-uuid-3"
  ]
}

// Lokale Rolle
{
  "name": "Shop Manager",
  "description": "Verwaltet Shop-Produkte",
  "scope": "local",
  "website": "website-uuid",
  "permissions": [
    "permission-uuid-1",
    "permission-uuid-2"
  ]
}
```

---

### Rolle einem Benutzer zuweisen

**Endpoint:** `POST /api/roles/{role_id}/assign/`  
**Berechtigung:** IsAdminUser

```javascript
// Globale Rolle zuweisen
{
  "user_id": "user-uuid"
}

// Lokale Rolle zuweisen
{
  "user_id": "user-uuid",
  "website_id": "website-uuid"
}
```

**Mehrere Rollen pro Benutzer:**
```javascript
// Benutzer kann mehrere Rollen haben
await assignRole('admin-role-uuid', userId);
await assignRole('editor-role-uuid', userId);
await assignRole('moderator-role-uuid', userId);
```

---

### Rolle von Benutzer entfernen

**Endpoint:** `POST /api/roles/{role_id}/revoke/`  
**Berechtigung:** IsAdminUser

```javascript
{
  "user_id": "user-uuid",
  "website_id": "website-uuid"  // Optional, nur bei lokalen Rollen
}
```

---

### Einzelne Permission zuweisen

**Endpoint:** `POST /api/permissions/user/{user_id}/assign/`  
**Berechtigung:** IsAdminUser

```javascript
{
  "permission_id": "permission-uuid",
  "website_id": "website-uuid"  // Optional, nur bei lokalen Permissions
}
```

---

### Benutzer-Permissions prüfen

**Endpoint:** `GET /api/permissions/check/{user_id}/`  
**Berechtigung:** IsAuthenticated  
**Query Parameters:** `?website=<uuid>`

```javascript
// Response (200 OK)
{
  "user_id": "uuid",
  "permissions": [
    {
      "code": "users.view",
      "name": "Benutzer anzeigen",
      "scope": "global",
      "source": "role",
      "role": "Administrator"
    },
    {
      "code": "posts.edit",
      "name": "Beiträge bearbeiten",
      "scope": "local",
      "website": "Blog Website",
      "source": "direct"
    }
  ]
}
```

**Eigene Permissions prüfen:**
```javascript
// Endpoint: GET /api/permissions/check/me/

const response = await fetch('/api/permissions/check/me/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const { permissions } = await response.json();
```

**Frontend Beispiel:**
```javascript
async function hasPermission(permissionCode) {
  const response = await fetch('/api/permissions/check/me/', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  const data = await response.json();
  return data.permissions.some(p => p.code === permissionCode);
}

// Verwendung
if (await hasPermission('users.delete')) {
  // Zeige "Löschen"-Button
}
```

---

### Spezifische Permission prüfen

**Endpoint:** `POST /api/permissions/check-permission/`  
**Berechtigung:** IsAuthenticated

```javascript
// Request
{
  "user_id": "user-uuid",
  "permission_code": "users.delete",
  "website_id": "website-uuid"  // Optional
}

// Response (200 OK)
{
  "has_permission": true,
  "source": "role",
  "role": "Administrator"
}
```

**Frontend Beispiel:**
```javascript
async function checkPermission(permissionCode, websiteId = null) {
  const response = await fetch('/api/permissions/check-permission/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
      permission_code: permissionCode,
      website_id: websiteId
    })
  });
  
  const data = await response.json();
  return data.has_permission;
}

// Verwendung
if (await checkPermission('products.delete', websiteId)) {
  showDeleteButton();
}
```

---

## 🔗 Social Login

### Verfügbare Provider

- Google (`/accounts/google/login/`)
- Facebook (`/accounts/facebook/login/`)
- GitHub (`/accounts/github/login/`)
- Microsoft (`/accounts/microsoft/login/`)
- Apple (`/accounts/apple/login/`)

### Social Login Flow

```javascript
// 1. Zur Social Login URL weiterleiten
window.location.href = 'http://localhost:8000/accounts/google/login/';

// 2. Nach erfolgreichem Login kommt der Benutzer zum callback_url zurück
// 3. JWT-Tokens werden in der Antwort zurückgegeben

// 4. Profil-Vollständigkeit prüfen
const profileStatus = await fetch('/api/accounts/check-profile/<website-id>/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const data = await profileStatus.json();

if (!data.completed) {
  // 5. Zeige Formular zum Vervollständigen des Profils
  showCompleteProfileForm(data.missing_fields);
}
```

---

### Verknüpfte Social-Accounts anzeigen

**Endpoint:** `GET /api/accounts/social-accounts/`  
**Berechtigung:** IsAuthenticated

```javascript
// Response (200 OK)
[
  {
    "id": "uuid",
    "provider": "google",
    "provider_account_id": "google-user-id-123",
    "email": "user@gmail.com",
    "name": "Max Mustermann",
    "created_at": "2025-01-01T10:00:00Z"
  }
]
```

---

## 📊 Sessions

### Aktive Sessions anzeigen

**Endpoint:** `GET /api/accounts/sessions/`  
**Berechtigung:** IsAuthenticated

```javascript
// Response (200 OK)
[
  {
    "id": "uuid",
    "user": "user@example.com",
    "website": "Meine Website",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "is_active": true,
    "created_at": "2025-12-22T10:00:00Z",
    "last_activity": "2025-12-22T14:30:00Z",
    "expires_at": "2025-12-23T10:00:00Z"
  }
]
```

---

## 🛠️ Best Practices

### 1. Token-Management

```javascript
// Token-Service erstellen
class AuthService {
  static getAccessToken() {
    return localStorage.getItem('access_token');
  }
  
  static getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }
  
  static setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }
  
  static clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
  
  static async refreshAccessToken() {
    const response = await fetch('/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: this.getRefreshToken() })
    });
    
    if (!response.ok) {
      this.clearTokens();
      window.location.href = '/login';
      throw new Error('Token refresh failed');
    }
    
    const data = await response.json();
    this.setTokens(data.access, this.getRefreshToken());
    return data.access;
  }
}
```

---

### 2. API-Client mit Auto-Refresh

```javascript
class ApiClient {
  static async fetch(url, options = {}) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${AuthService.getAccessToken()}`
    };
    
    let response = await fetch(url, options);
    
    // Auto-refresh bei 401
    if (response.status === 401) {
      await AuthService.refreshAccessToken();
      
      options.headers['Authorization'] = `Bearer ${AuthService.getAccessToken()}`;
      response = await fetch(url, options);
    }
    
    return response;
  }
}

// Verwendung
const data = await ApiClient.fetch('/api/accounts/profile/');
```

---

### 3. Permission-Caching

```javascript
class PermissionService {
  static cache = null;
  static cacheTime = null;
  static CACHE_DURATION = 5 * 60 * 1000; // 5 Minuten
  
  static async getPermissions(forceRefresh = false) {
    const now = Date.now();
    
    if (!forceRefresh && this.cache && (now - this.cacheTime < this.CACHE_DURATION)) {
      return this.cache;
    }
    
    const response = await ApiClient.fetch('/api/permissions/check/me/');
    const data = await response.json();
    
    this.cache = data.permissions;
    this.cacheTime = now;
    
    return this.cache;
  }
  
  static async hasPermission(code) {
    const permissions = await this.getPermissions();
    return permissions.some(p => p.code === code);
  }
  
  static clearCache() {
    this.cache = null;
    this.cacheTime = null;
  }
}

// Nach Login Cache leeren
await AuthService.login(email, password);
PermissionService.clearCache();
```

---

### 4. React Hook für Permissions

```javascript
import { useState, useEffect } from 'react';

function usePermissions() {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadPermissions() {
      const perms = await PermissionService.getPermissions();
      setPermissions(perms);
      setLoading(false);
    }
    loadPermissions();
  }, []);
  
  const hasPermission = (code) => {
    return permissions.some(p => p.code === code);
  };
  
  return { permissions, hasPermission, loading };
}

// Verwendung
function UserList() {
  const { hasPermission, loading } = usePermissions();
  
  if (loading) return <div>Lade...</div>;
  
  return (
    <div>
      <h1>Benutzer</h1>
      {hasPermission('users.delete') && (
        <button>Benutzer löschen</button>
      )}
    </div>
  );
}
```

---

## 🚨 Fehlerbehandlung

### Standard-Fehlerformate

```javascript
// 400 Bad Request
{
  "error": "Validation error",
  "details": {
    "email": ["This field is required."],
    "password": ["Password too short."]
  }
}

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}

// 404 Not Found
{
  "detail": "Not found."
}
```

### Fehlerbehandlung im Frontend

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      if (response.status === 401) {
        // Nicht authentifiziert
        window.location.href = '/login';
      } else if (response.status === 403) {
        // Keine Berechtigung
        alert('Keine Berechtigung für diese Aktion');
      } else if (response.status === 404) {
        // Nicht gefunden
        alert('Ressource nicht gefunden');
      } else {
        // Sonstige Fehler
        alert(data.error || 'Ein Fehler ist aufgetreten');
      }
      throw new Error(data.error);
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

---

## 📞 Support

Bei Fragen oder Problemen:
- Siehe [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) für detaillierte Permissions-Erklärungen
- Siehe [QUICK_START.md](QUICK_START.md) für schnellen Einstieg
- Siehe [FRONTEND_PERMISSIONS.md](FRONTEND_PERMISSIONS.md) für Frontend-Integration
