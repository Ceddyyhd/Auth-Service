# Single Sign-On (SSO) System

## Übersicht

Das SSO-System ermöglicht es Benutzern, sich einmal beim Auth-Service anzumelden und automatisch auf allen verbundenen Websites angemeldet zu sein. Kein erneutes Login erforderlich!

## 🎯 Funktionsweise

```
User besucht Website B
    ↓
Website B prüft: Hat User Session?
    ↓ Nein
Website B → Redirect zu Auth-Service SSO
    ↓
Auth-Service prüft: Ist User angemeldet?
    ↓ Ja (Session Cookie vorhanden)
Auth-Service generiert SSO-Token
    ↓
Redirect zurück zu Website B mit Token
    ↓
Website B tauscht Token gegen JWT
    ↓
User ist auf Website B angemeldet! ✅
```

---

## API Endpoints

### 1. SSO Status prüfen

**Endpoint:** `POST /api/accounts/sso/status/`

**Berechtigung:** Keine (Public)

**Beschreibung:** Prüft, ob ein Benutzer eine aktive SSO-Session hat.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/sso/status/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "website_id": "your-website-uuid"
  }'
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

### 2. SSO initiieren

**Endpoint:** `GET /api/accounts/sso/initiate/`

**Berechtigung:** Keine (Public)

**Beschreibung:** Startet den SSO-Flow. Gibt SSO-Token zurück wenn User angemeldet ist, sonst Login-URL.

**Query Parameters:**
- `website_id`: UUID der Website
- `return_url`: URL für Redirect nach SSO

**Request:**
```bash
curl -X GET "http://localhost:8000/api/accounts/sso/initiate/?website_id=YOUR_WEBSITE_ID&return_url=https://yourwebsite.com/auth/callback" \
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
  "login_url": "http://localhost:3000/login?website_id=YOUR_WEBSITE_ID&return_url=https://yourwebsite.com/auth/callback",
  "message": "User must login first"
}
```

---

### 3. SSO Token austauschen

**Endpoint:** `POST /api/accounts/sso/exchange/`

**Berechtigung:** Keine (Public, aber Token-validiert)

**Beschreibung:** Tauscht SSO-Token gegen JWT Access/Refresh Tokens.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/sso/exchange/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "sso_token": "token_from_initiate_endpoint",
    "website_id": "your-website-uuid"
  }'
```

**Response:**
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLC...",
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "website": {
    "id": "website-uuid",
    "name": "My Website"
  }
}
```

**Fehler-Response:**
```json
{
  "error": "Invalid SSO token"
}
```

```json
{
  "error": "SSO token has expired or already been used"
}
```

---

### 4. SSO Login Callback

**Endpoint:** `POST /api/accounts/sso/callback/`

**Berechtigung:** Keine (Public)

**Beschreibung:** Nach Login im Auth-Service generiert dieser Endpoint einen SSO-Token für Website-Redirect.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/sso/callback/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "website_id": "your-website-uuid",
    "return_url": "https://yourwebsite.com/auth/callback",
    "refresh_token": "refresh_token_from_login"
  }'
```

**Response:**
```json
{
  "success": true,
  "sso_token": "newly_generated_sso_token",
  "redirect_url": "https://yourwebsite.com/auth/callback?sso_token=newly_generated_sso_token",
  "expires_in": 300
}
```

---

### 5. SSO Logout

**Endpoint:** `GET /api/accounts/sso/logout/`

**Berechtigung:** Keine (Public)

**Beschreibung:** Meldet Benutzer von ALLEN Websites ab. Invalidiert alle SSO-Tokens und löscht Session.

**Query Parameters:**
- `return_url`: URL für Redirect nach Logout (optional)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/accounts/sso/logout/?return_url=https://yourwebsite.com" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out from all websites",
  "redirect_url": "https://yourwebsite.com"
}
```

---

## Frontend Integration

### React/Next.js Beispiel

#### 1. SSO Helper Klasse erstellen

```javascript
// utils/sso.js
class SSOManager {
  constructor(authServiceUrl, websiteId, apiKey) {
    this.authServiceUrl = authServiceUrl;
    this.websiteId = websiteId;
    this.apiKey = apiKey;
  }

  async checkSSOStatus() {
    const response = await fetch(`${this.authServiceUrl}/api/accounts/sso/status/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      },
      body: JSON.stringify({
        website_id: this.websiteId
      }),
      credentials: 'include'  // WICHTIG: Session Cookie mitschicken
    });

    return await response.json();
  }

  async initiateSSO(returnUrl) {
    const url = new URL(`${this.authServiceUrl}/api/accounts/sso/initiate/`);
    url.searchParams.append('website_id', this.websiteId);
    url.searchParams.append('return_url', returnUrl);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'X-API-Key': this.apiKey
      },
      credentials: 'include'  // WICHTIG: Session Cookie mitschicken
    });

    return await response.json();
  }

  async exchangeToken(ssoToken) {
    const response = await fetch(`${this.authServiceUrl}/api/accounts/sso/exchange/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey
      },
      body: JSON.stringify({
        sso_token: ssoToken,
        website_id: this.websiteId
      })
    });

    if (!response.ok) {
      throw new Error('Failed to exchange SSO token');
    }

    return await response.json();
  }

  async logout(returnUrl = '/') {
    const url = new URL(`${this.authServiceUrl}/api/accounts/sso/logout/`);
    url.searchParams.append('return_url', returnUrl);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'X-API-Key': this.apiKey
      },
      credentials: 'include'
    });

    return await response.json();
  }
}

export default SSOManager;
```

---

#### 2. SSO in Ihrer App implementieren

```javascript
// pages/_app.js oder App.js
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import SSOManager from '../utils/sso';

const ssoManager = new SSOManager(
  'http://localhost:8000',
  'your-website-uuid',
  'your-api-key'
);

function MyApp({ Component, pageProps }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    handleSSO();
  }, []);

  async function handleSSO() {
    // Schritt 1: Prüfen ob SSO-Token in URL vorhanden
    const urlParams = new URLSearchParams(window.location.search);
    const ssoToken = urlParams.get('sso_token');

    if (ssoToken) {
      // Token austauschen
      try {
        const data = await ssoManager.exchangeToken(ssoToken);
        
        // Tokens speichern
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        setIsAuthenticated(true);
        
        // URL bereinigen (Token entfernen)
        const cleanUrl = window.location.pathname;
        router.replace(cleanUrl);
      } catch (error) {
        console.error('SSO token exchange failed:', error);
      }
    } else {
      // Schritt 2: Prüfen ob Benutzer bereits lokale Tokens hat
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        setIsAuthenticated(true);
        setLoading(false);
        return;
      }

      // Schritt 3: Prüfen ob SSO verfügbar ist
      try {
        const status = await ssoManager.checkSSOStatus();
        
        if (status.sso_available && status.authenticated) {
          // User ist im Auth-Service angemeldet, SSO initiieren
          const returnUrl = window.location.href;
          const result = await ssoManager.initiateSSO(returnUrl);
          
          if (result.authenticated && result.sso_token) {
            // SSO Token erhalten, austauschen
            const data = await ssoManager.exchangeToken(result.sso_token);
            
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            setIsAuthenticated(true);
          }
        }
      } catch (error) {
        console.error('SSO check failed:', error);
      }
    }
    
    setLoading(false);
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  return <Component {...pageProps} isAuthenticated={isAuthenticated} />;
}

export default MyApp;
```

---

#### 3. Login-Seite mit SSO

```javascript
// pages/login.js
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import SSOManager from '../utils/sso';

const ssoManager = new SSOManager(
  'http://localhost:8000',
  'your-website-uuid',
  'your-api-key'
);

export default function Login() {
  const router = useRouter();

  useEffect(() => {
    checkSSO();
  }, []);

  async function checkSSO() {
    // Prüfen ob SSO verfügbar
    const status = await ssoManager.checkSSOStatus();
    
    if (status.sso_available) {
      // User bereits angemeldet, direkt SSO
      const returnUrl = window.location.origin + '/dashboard';
      const result = await ssoManager.initiateSSO(returnUrl);
      
      if (result.redirect_url) {
        window.location.href = result.redirect_url;
      }
    }
  }

  function handleLogin() {
    // Zum Auth-Service Login redirecten
    const returnUrl = window.location.origin + '/auth/callback';
    const loginUrl = `http://localhost:8000/login?website_id=your-website-uuid&return_url=${encodeURIComponent(returnUrl)}`;
    window.location.href = loginUrl;
  }

  return (
    <div>
      <h1>Login</h1>
      <button onClick={handleLogin}>
        Mit Auth-Service anmelden
      </button>
    </div>
  );
}
```

---

#### 4. Callback-Seite

```javascript
// pages/auth/callback.js
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import SSOManager from '../../utils/sso';

const ssoManager = new SSOManager(
  'http://localhost:8000',
  'your-website-uuid',
  'your-api-key'
);

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    handleCallback();
  }, []);

  async function handleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const ssoToken = urlParams.get('sso_token');

    if (!ssoToken) {
      router.push('/login');
      return;
    }

    try {
      const data = await ssoManager.exchangeToken(ssoToken);
      
      // Tokens speichern
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect zu Dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error('Authentication failed:', error);
      router.push('/login');
    }
  }

  return <div>Authentifizierung läuft...</div>;
}
```

---

#### 5. Logout mit SSO

```javascript
// components/LogoutButton.js
import SSOManager from '../utils/sso';

const ssoManager = new SSOManager(
  'http://localhost:8000',
  'your-website-uuid',
  'your-api-key'
);

export default function LogoutButton() {
  async function handleLogout() {
    // Lokale Tokens löschen
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    // SSO Logout (von allen Websites)
    const returnUrl = window.location.origin;
    await ssoManager.logout(returnUrl);

    // Redirect zu Homepage
    window.location.href = '/';
  }

  return (
    <button onClick={handleLogout}>
      Abmelden
    </button>
  );
}
```

---

## Vanilla JavaScript Beispiel

```html
<!DOCTYPE html>
<html>
<head>
  <title>SSO Demo</title>
</head>
<body>
  <div id="app">
    <div id="loading">Prüfe Anmeldung...</div>
    <div id="authenticated" style="display: none;">
      <h1>Willkommen, <span id="username"></span>!</h1>
      <button onclick="logout()">Abmelden</button>
    </div>
    <div id="not-authenticated" style="display: none;">
      <h1>Bitte anmelden</h1>
      <button onclick="login()">Anmelden</button>
    </div>
  </div>

  <script>
    const AUTH_SERVICE = 'http://localhost:8000';
    const WEBSITE_ID = 'your-website-uuid';
    const API_KEY = 'your-api-key';

    // SSO prüfen beim Seitenaufruf
    window.addEventListener('load', async () => {
      await handleSSO();
    });

    async function handleSSO() {
      // 1. SSO Token in URL?
      const urlParams = new URLSearchParams(window.location.search);
      const ssoToken = urlParams.get('sso_token');

      if (ssoToken) {
        // Token austauschen
        const data = await exchangeToken(ssoToken);
        if (data) {
          saveTokens(data);
          showAuthenticated(data.user);
          // URL bereinigen
          window.history.replaceState({}, '', window.location.pathname);
          return;
        }
      }

      // 2. Lokale Tokens vorhanden?
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        const user = JSON.parse(localStorage.getItem('user'));
        showAuthenticated(user);
        return;
      }

      // 3. SSO Status prüfen
      const status = await checkSSOStatus();
      if (status.sso_available && status.authenticated) {
        // SSO initiieren
        const result = await initiateSSO(window.location.href);
        if (result.sso_token) {
          const data = await exchangeToken(result.sso_token);
          saveTokens(data);
          showAuthenticated(data.user);
          return;
        }
      }

      // Nicht angemeldet
      showNotAuthenticated();
    }

    async function checkSSOStatus() {
      const response = await fetch(`${AUTH_SERVICE}/api/accounts/sso/status/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        },
        body: JSON.stringify({ website_id: WEBSITE_ID }),
        credentials: 'include'
      });
      return await response.json();
    }

    async function initiateSSO(returnUrl) {
      const url = `${AUTH_SERVICE}/api/accounts/sso/initiate/?website_id=${WEBSITE_ID}&return_url=${encodeURIComponent(returnUrl)}`;
      const response = await fetch(url, {
        headers: { 'X-API-Key': API_KEY },
        credentials: 'include'
      });
      return await response.json();
    }

    async function exchangeToken(ssoToken) {
      const response = await fetch(`${AUTH_SERVICE}/api/accounts/sso/exchange/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        },
        body: JSON.stringify({
          sso_token: ssoToken,
          website_id: WEBSITE_ID
        })
      });
      
      if (!response.ok) return null;
      return await response.json();
    }

    function saveTokens(data) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    function login() {
      const returnUrl = window.location.href;
      window.location.href = `http://localhost:3000/login?website_id=${WEBSITE_ID}&return_url=${encodeURIComponent(returnUrl)}`;
    }

    async function logout() {
      localStorage.clear();
      
      const response = await fetch(`${AUTH_SERVICE}/api/accounts/sso/logout/?return_url=${window.location.origin}`, {
        headers: { 'X-API-Key': API_KEY },
        credentials: 'include'
      });
      
      window.location.reload();
    }

    function showAuthenticated(user) {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('not-authenticated').style.display = 'none';
      document.getElementById('authenticated').style.display = 'block';
      document.getElementById('username').textContent = user.email;
    }

    function showNotAuthenticated() {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('authenticated').style.display = 'none';
      document.getElementById('not-authenticated').style.display = 'block';
    }
  </script>
</body>
</html>
```

---

## Technische Details

### SSO-Token Eigenschaften

- **Format:** URL-safe Base64 String (32 Bytes)
- **Gültigkeit:** 5 Minuten
- **Einmalig:** Token wird nach Verwendung invalidiert
- **Sicherheit:** Gebunden an IP und User-Agent (optional)

### Session-Verwaltung

- **Cookie:** `sessionid` (HttpOnly, SameSite=Lax)
- **Dauer:** 7 Tage (konfigurierbar)
- **Domain:** Kann für Subdomain-Sharing konfiguriert werden
- **Aktualisierung:** Bei jedem Request erneuert

### Sicherheitsmerkmale

1. **Token-Expiry:** Tokens verfallen nach 5 Minuten
2. **One-Time-Use:** Jeder Token nur einmal verwendbar
3. **IP-Tracking:** Optionale IP-Validierung
4. **User-Agent-Check:** Browser-Fingerprinting
5. **HTTPS Required:** In Produktion nur über HTTPS

---

## CORS-Konfiguration

Für SSO zwischen verschiedenen Domains benötigen Sie CORS:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://website-a.com",
    "https://website-b.com",
    "https://website-c.com",
]

CORS_ALLOW_CREDENTIALS = True  # WICHTIG für Session Cookies!

# Für Entwicklung:
CORS_ALLOW_ALL_ORIGINS = True  # NUR für Entwicklung!
```

---

## Production Setup

### 1. HTTPS erzwingen

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Cookie-Domain konfigurieren

```python
# Für Subdomain-Sharing
SESSION_COOKIE_DOMAIN = '.yourdomain.com'
# Dann funktioniert SSO zwischen:
# - auth.yourdomain.com
# - app.yourdomain.com
# - shop.yourdomain.com
```

### 3. Session-Backend optimieren

```python
# Redis für bessere Performance
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.client.DefaultClient',
        'LOCATION': 'redis://localhost:6379/1',
    }
}
```

---

## Troubleshooting

### Problem: "SSO token has expired"

**Ursache:** Token älter als 5 Minuten oder bereits verwendet

**Lösung:**
- Neues SSO initiieren
- Token-Expiry in Settings erhöhen (nicht empfohlen)
- Prüfen, ob Token mehrfach verwendet wird

### Problem: Session Cookie wird nicht mitgesendet

**Ursache:** CORS oder Cookie-Einstellungen falsch

**Lösung:**
```javascript
// credentials: 'include' hinzufügen
fetch(url, {
  credentials: 'include'
})
```

```python
# settings.py
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Nicht 'Strict'!
```

### Problem: SSO funktioniert nicht zwischen Domains

**Ursache:** Cookies funktionieren nicht cross-domain

**Lösung:**
1. Verwenden Sie Subdomains (.yourdomain.com)
2. Oder: Redirect-basiertes SSO (bereits implementiert)

### Problem: User wird nicht automatisch angemeldet

**Prüfen:**
1. Session Cookie vorhanden? (Browser DevTools → Application → Cookies)
2. CORS richtig konfiguriert?
3. `credentials: 'include'` bei Fetch?
4. SSO Status Endpoint aufgerufen?

---

## Best Practices

### Für Entwickler:

1. **Session Cookies richtig setzen**
   - `HttpOnly`: Schutz vor XSS
   - `SameSite=Lax`: Erlaubt SSO-Redirects
   - `Secure`: Nur über HTTPS (Production)

2. **Token-Handling**
   - Tokens sofort nach Erhalt austauschen
   - Keine Tokens in Logs oder Errors speichern
   - URL nach Token-Austausch bereinigen

3. **Error-Handling**
   - Graceful Fallback auf Login-Seite
   - Expired-Token-Error abfangen
   - User-Feedback bei Problemen

### Für Benutzer:

1. **Cookies erlauben**
   - SSO funktioniert nur mit Cookies
   - Third-Party-Cookies nicht nötig

2. **Ein Browser, mehrere Websites**
   - SSO funktioniert im selben Browser
   - Inkognito-Modus = separate Session

3. **Logout**
   - SSO Logout meldet von ALLEN Websites ab
   - Lokaler Logout nur von aktueller Website

---

## Flowchart

```
┌─────────────────────────────────────────────────────────┐
│              User besucht Website B                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Lokale Tokens?       │
          └──────┬───────────────┘
                 │
         ┌───────┴────────┐
         │ Ja             │ Nein
         ▼                ▼
    ┌────────┐      ┌──────────────┐
    │ Fertig │      │ SSO prüfen   │
    └────────┘      └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │ SSO Status Endpoint │
                └──────────┬──────────┘
                           │
                    ┌──────┴─────┐
                    │ Angemeldet?│
                    └──────┬─────┘
                           │
                    ┌──────┴──────┐
            Nein    │             │ Ja
         ┌──────────┤             ├─────────┐
         │          │             │         │
         ▼          │             │         ▼
    ┌────────────┐  │             │  ┌─────────────┐
    │ Login-     │  │             │  │ SSO Initiate│
    │ Seite      │  │             │  └──────┬──────┘
    └────────────┘  │             │         │
                    │             │         ▼
                    │             │  ┌─────────────┐
                    │             │  │ SSO Token   │
                    │             │  └──────┬──────┘
                    │             │         │
                    │             │         ▼
                    │             │  ┌─────────────┐
                    │             │  │ Exchange    │
                    │             │  │ für JWT     │
                    │             │  └──────┬──────┘
                    │             │         │
                    │             │         ▼
                    │             │  ┌─────────────┐
                    │             │  │ Angemeldet! │
                    │             │  └─────────────┘
                    └─────────────┘
```

---

## Datenbankmodell

```python
class SSOToken(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    token = CharField(max_length=255, unique=True)
    website = ForeignKey(Website)
    created_at = DateTimeField()
    expires_at = DateTimeField()
    is_used = BooleanField(default=False)
    used_at = DateTimeField(null=True)
    ip_address = GenericIPAddressField()
    user_agent = TextField()
```

---

## Testing

### Manueller Test

1. **User auf Website A anmelden**
2. **Website B öffnen** (im selben Browser)
3. **Automatisch angemeldet!** ✅

### Test-Szenario

```javascript
// 1. Login auf Website A
await login('user@example.com', 'password');

// 2. Website B besuchen
window.location.href = 'https://website-b.com';

// 3. Website B prüft SSO
const status = await checkSSOStatus();
// status.authenticated === true

// 4. SSO initiieren
const result = await initiateSSO();
// result.sso_token vorhanden

// 5. Token austauschen
const auth = await exchangeToken(result.sso_token);
// auth.access & auth.refresh erhalten

// 6. Fertig! User angemeldet auf Website B
```

---

## Häufige Fragen (FAQ)

**Q: Funktioniert SSO über verschiedene Browser?**
A: Nein, SSO basiert auf Session Cookies, die pro Browser getrennt sind.

**Q: Wie lange dauert SSO?**
A: Nahezu instant - ca. 200-500ms für Token-Austausch.

**Q: Was passiert bei Session-Ablauf?**
A: User muss sich erneut anmelden, dann funktioniert SSO wieder.

**Q: Kann ich SSO deaktivieren?**
A: Ja, einfach SSO-Endpoints nicht aufrufen und normales Login verwenden.

**Q: Funktioniert SSO mit Mobile Apps?**
A: Ja, mit OAuth2 Redirect-Flow oder Deep Links.

---

**Stand:** Dezember 2025
**Version:** 1.0
**Autor:** Auth Service Team
