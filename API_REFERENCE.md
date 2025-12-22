# 📚 API-Referenz - Auth Service

Vollständige API-Dokumentation für den zentralen Authentication Service.

## 📋 Inhaltsverzeichnis

- [Authentifizierung](#authentifizierung)
- [Benutzer-Verwaltung](#benutzer-verwaltung)
- [Website-Verwaltung](#website-verwaltung)
- [Permissions & Rollen](#permissions--rollen)
- [Social Login](#social-login)
- [Sessions](#sessions)

---

## 🔐 Authentifizierung

### Registrierung

**Endpoint:** `POST /api/accounts/register/`  
**Berechtigung:** Keine (öffentlich)

```javascript
// Request
{
  "email": "user@example.com",
  "username": "user123",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "first_name": "Max",
  "last_name": "Mustermann",
  "website_id": "website-uuid",
  
  // Optional (je nach Website-Einstellungen):
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "date_of_birth": "1990-01-01",
  "company": "Meine Firma GmbH"
}

// Response (201 Created)
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user123",
    "first_name": "Max",
    "last_name": "Mustermann",
    "profile_completed": true
  },
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  },
  "message": "Benutzer erfolgreich registriert."
}
```

**Frontend Beispiel:**
```javascript
async function register(userData) {
  const response = await fetch('http://localhost:8000/api/accounts/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.tokens.access);
  localStorage.setItem('refresh_token', data.tokens.refresh);
  
  return data;
}
```

---

### Login

**Endpoint:** `POST /api/accounts/login/`  
**Berechtigung:** Keine (öffentlich)

```javascript
// Request
{
  "username": "user@example.com",  // oder username
  "password": "SecurePassword123!"
}

// Response (200 OK)
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Frontend Beispiel:**
```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}

// Token verwenden
fetch('http://localhost:8000/api/accounts/profile/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

---

### Logout

**Endpoint:** `POST /api/accounts/logout/`  
**Berechtigung:** IsAuthenticated

```javascript
// Request
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

// Response (200 OK)
{
  "message": "Erfolgreich abgemeldet."
}
```

**Frontend Beispiel:**
```javascript
async function logout() {
  await fetch('http://localhost:8000/api/accounts/logout/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({ 
      refresh: localStorage.getItem('refresh_token') 
    })
  });
  
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}
```

---

### Token Refresh

**Endpoint:** `POST /api/token/refresh/`  
**Berechtigung:** Keine

```javascript
// Request
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

// Response (200 OK)
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Frontend Beispiel (Axios Interceptor):**
```javascript
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      
      try {
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken
        });
        
        localStorage.setItem('access_token', response.data.access);
        error.config.headers['Authorization'] = `Bearer ${response.data.access}`;
        
        return axios(error.config);
      } catch (refreshError) {
        // Refresh fehlgeschlagen - Logout
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 👤 Benutzer-Verwaltung

### Profil abrufen

**Endpoint:** `GET /api/accounts/profile/`  
**Berechtigung:** IsAuthenticated

```javascript
// Response (200 OK)
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user123",
  "first_name": "Max",
  "last_name": "Mustermann",
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "date_of_birth": "1990-01-01",
  "company": "Meine Firma GmbH",
  "profile_completed": true,
  "is_verified": true,
  "is_active": true,
  "date_joined": "2025-01-01T10:00:00Z"
}
```

---

### Profil aktualisieren

**Endpoint:** `PATCH /api/accounts/profile/`  
**Berechtigung:** IsAuthenticated

```javascript
// Request
{
  "first_name": "Maximilian",
  "phone": "+49987654321",
  "city": "München"
}

// Response (200 OK)
{
  "id": "uuid",
  "first_name": "Maximilian",
  "phone": "+49987654321",
  "city": "München",
  ...
}
```

---

### Passwort ändern

**Endpoint:** `POST /api/accounts/change-password/`  
**Berechtigung:** IsAuthenticated

```javascript
// Request
{
  "old_password": "AltesPaßw0rt!",
  "new_password": "NeuesPaßw0rt!",
  "new_password_confirm": "NeuesPaßw0rt!"
}

// Response (200 OK)
{
  "message": "Passwort erfolgreich geändert."
}
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
