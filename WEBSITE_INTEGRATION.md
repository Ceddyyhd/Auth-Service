# 🌐 Website-Integration - Schritt für Schritt

Diese Anleitung zeigt dir, wie du eine Website mit dem Auth Service verbindest.

---

## 📋 Was du von der Website bekommst

Nachdem du eine Website im Admin-Panel registriert hast, erhältst du:

### 1. **Website-ID** (UUID)
```
Beispiel: 550e8400-e29b-41d4-a716-446655440000
```
- Eindeutige Identifikation deiner Website
- Wird bei Registrierung/Login übergeben

### 2. **API Key** (öffentlich)
```
Beispiel: pk_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```
- **Verwendung:** Client-seitig (JavaScript im Browser)
- Prefix: `pk_` (public key)
- Für öffentliche API-Anfragen
- **⚠️ Kann im Frontend-Code sichtbar sein**

### 3. **API Secret** (privat)
```
Beispiel: sk_xyz987wvu654tsr321qpo098nml876kji543hgf210edc
```
- **Verwendung:** NUR Server-seitig (Backend)
- Prefix: `sk_` (secret key)
- Für Token-Validierung und sichere Operationen
- **🔒 NIEMALS im Frontend verwenden!**

### 4. **Client ID & Client Secret**
```
Client ID: web_550e8400e29b41d4a716
Client Secret: secret_abc123def456
```
- Für OAuth2-Flow
- Nur bei OAuth2-Integration nötig

---

## 🚀 Schnellstart: Website registrieren

### 1. Im Admin-Panel anmelden
```
http://localhost:8000/admin/
```

### 2. Neue Website erstellen
```
Admin → Websites → Website hinzufügen
```

**Eingaben:**
- **Name:** Meine Website
- **Domain:** example.com
- **Callback URL:** https://example.com/auth/callback
- **Allowed Origins:** `["https://example.com", "http://localhost:3000"]`
- **Pflichtfelder:** Aktiviere benötigte Felder (Vorname, Nachname, etc.)

### 3. Credentials kopieren
Nach dem Speichern werden automatisch generiert:
- ✅ API Key (`pk_...`)
- ✅ API Secret (`sk_...`)
- ✅ Client ID
- ✅ Client Secret

**⚠️ WICHTIG:** Kopiere das **API Secret** sofort - es wird aus Sicherheitsgründen später verschleiert angezeigt!

---

## 💻 Frontend-Integration (JavaScript)

### Setup: API Key einbinden

```html
<!-- In deinem HTML -->
<script>
  const AUTH_SERVICE_URL = 'http://localhost:8000';
  const WEBSITE_ID = '550e8400-e29b-41d4-a716-446655440000';
  const API_KEY = 'pk_abc123def456...'; // Öffentlicher API Key
</script>
```

### Beispiel: Benutzer registrieren

```javascript
async function registerUser(userData) {
  const response = await fetch(`${AUTH_SERVICE_URL}/api/accounts/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,  // API Key im Header
    },
    body: JSON.stringify({
      ...userData,
      website_id: WEBSITE_ID,
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Tokens speichern
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    return data;
  }
  
  throw new Error(data.error || 'Registrierung fehlgeschlagen');
}
```

### Beispiel: Login

```javascript
async function login(email, password) {
  const response = await fetch(`${AUTH_SERVICE_URL}/api/accounts/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({
      username: email,
      password: password,
      website_id: WEBSITE_ID,
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  }
  
  throw new Error('Login fehlgeschlagen');
}
```

### Beispiel: API-Anfragen mit Token

```javascript
async function getProfile() {
  const response = await fetch(`${AUTH_SERVICE_URL}/api/accounts/profile/`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'X-API-Key': API_KEY,
    }
  });
  
  return await response.json();
}
```

---

## 🔧 Backend-Integration (Server-seitig)

### Verwendung des API Secrets

**⚠️ NUR im Backend verwenden!**

```javascript
// Node.js Backend-Beispiel
const express = require('express');
const axios = require('axios');

const AUTH_SERVICE_URL = 'http://localhost:8000';
const WEBSITE_ID = '550e8400-e29b-41d4-a716-446655440000';
const API_SECRET = process.env.AUTH_API_SECRET; // sk_...

app.post('/api/verify-token', async (req, res) => {
  const { token } = req.body;
  
  try {
    // Token beim Auth Service verifizieren
    const response = await axios.post(
      `${AUTH_SERVICE_URL}/api/auth/verify-token/`,
      {
        token: token,
        website_id: WEBSITE_ID,
      },
      {
        headers: {
          'X-API-Secret': API_SECRET,  // Secret Key für Server-zu-Server
        }
      }
    );
    
    if (response.data.valid) {
      res.json({ 
        valid: true, 
        user: response.data.user 
      });
    } else {
      res.status(401).json({ valid: false });
    }
  } catch (error) {
    res.status(500).json({ error: 'Token-Verifizierung fehlgeschlagen' });
  }
});
```

### Python/Django Backend

```python
import requests
import os

AUTH_SERVICE_URL = 'http://localhost:8000'
WEBSITE_ID = '550e8400-e29b-41d4-a716-446655440000'
API_SECRET = os.getenv('AUTH_API_SECRET')  # sk_...

def verify_user_token(token):
    """Verifiziert ein User-Token beim Auth Service."""
    response = requests.post(
        f'{AUTH_SERVICE_URL}/api/auth/verify-token/',
        json={
            'token': token,
            'website_id': WEBSITE_ID,
        },
        headers={
            'X-API-Secret': API_SECRET,
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('valid'), data.get('user')
    
    return False, None

# Middleware für geschützte Routen
def require_auth(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Nicht authentifiziert'}, status=401)
        
        token = auth_header.split(' ')[1]
        valid, user = verify_user_token(token)
        
        if not valid:
            return JsonResponse({'error': 'Ungültiges Token'}, status=401)
        
        request.auth_user = user
        return view_func(request, *args, **kwargs)
    
    return wrapper
```

---

## 🔐 Sicherheits-Best-Practices

### ✅ DO's (Mache das)

1. **API Key (`pk_`) im Frontend verwenden**
   ```javascript
   // ✅ OK - Öffentlich sichtbar
   headers: { 'X-API-Key': 'pk_abc123...' }
   ```

2. **API Secret (`sk_`) NUR im Backend**
   ```javascript
   // ✅ OK - Server-seitig
   const API_SECRET = process.env.AUTH_API_SECRET;
   ```

3. **Umgebungsvariablen für Secrets**
   ```bash
   # .env Datei
   AUTH_API_SECRET=sk_xyz987...
   AUTH_WEBSITE_ID=550e8400-e29b-41d4-a716-446655440000
   ```

4. **Tokens sicher speichern**
   ```javascript
   // ✅ OK - LocalStorage für Tokens
   localStorage.setItem('access_token', token);
   
   // Oder besser: HttpOnly Cookies (serverseitig)
   res.cookie('auth_token', token, { 
     httpOnly: true, 
     secure: true,
     sameSite: 'strict'
   });
   ```

### ❌ DON'Ts (Mache das NICHT)

1. **API Secret im Frontend**
   ```javascript
   // ❌ NIEMALS! Secret ist kompromittiert!
   const API_SECRET = 'sk_xyz987...';
   ```

2. **Secrets in Git committen**
   ```bash
   # ❌ NIEMALS in git!
   # Füge .env zur .gitignore hinzu
   echo ".env" >> .gitignore
   ```

3. **Unverschlüsselte Übertragung**
   ```javascript
   // ❌ Nur HTTP in Production
   const AUTH_SERVICE_URL = 'http://example.com';
   
   // ✅ Immer HTTPS in Production
   const AUTH_SERVICE_URL = 'https://example.com';
   ```

---

## 📊 Website-Verwaltung per API

### Neue Website erstellen

```javascript
// Nur Admins!
async function createWebsite(websiteData) {
  const response = await fetch('http://localhost:8000/api/accounts/websites/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`,
    },
    body: JSON.stringify({
      name: 'Neue Website',
      domain: 'newsite.com',
      callback_url: 'https://newsite.com/auth/callback',
      allowed_origins: ['https://newsite.com'],
      require_first_name: true,
      require_last_name: true,
    })
  });
  
  const data = await response.json();
  
  // Credentials sofort speichern!
  console.log('Website ID:', data.id);
  console.log('API Key:', data.api_key);
  console.log('API Secret:', data.api_secret);
  console.log('Client ID:', data.client_id);
  console.log('Client Secret:', data.client_secret);
  
  return data;
}
```

### API Keys neu generieren

```python
# Im Django Admin oder via Management Command
from accounts.models import Website

website = Website.objects.get(domain='example.com')
website.regenerate_api_keys()

print(f'Neuer API Key: {website.api_key}')
print(f'Neues API Secret: {website.api_secret}')
```

---

## 🧪 Test-Setup

### 1. Lokales Testen

```bash
# Auth Service starten
cd Auth-Service
python manage.py runserver

# Test-Website (separates Projekt)
cd ../my-website
npm start  # oder dein Dev-Server
```

### 2. Test-Credentials erstellen

```bash
# Django Shell öffnen
python manage.py shell

# Test-Website erstellen
from accounts.models import Website

test_website = Website.objects.create(
    name='Test Website',
    domain='localhost:3000',
    callback_url='http://localhost:3000/auth/callback',
    allowed_origins=['http://localhost:3000'],
    require_first_name=True,
    require_last_name=True,
)

print(f'Website ID: {test_website.id}')
print(f'API Key: {test_website.api_key}')
print(f'API Secret: {test_website.api_secret}')
```

### 3. Postman/Insomnia Collection

```json
{
  "info": {
    "name": "Auth Service API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "api_key",
      "value": "pk_YOUR_API_KEY"
    },
    {
      "key": "website_id",
      "value": "YOUR_WEBSITE_ID"
    }
  ]
}
```

---

## 🆘 Troubleshooting

### Problem: "Invalid API Key"

**Lösung:**
```javascript
// Prüfe ob API Key korrekt ist
console.log('API Key:', API_KEY);
console.log('Startet mit pk_:', API_KEY.startsWith('pk_'));

// Prüfe Header
console.log('Headers:', {
  'X-API-Key': API_KEY,
});
```

### Problem: CORS-Fehler

**Lösung:**
```python
# settings.py - CORS konfigurieren
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://example.com",
]

# Oder in Website allowed_origins:
website.allowed_origins = ["http://localhost:3000"]
website.save()
```

### Problem: Token ungültig

**Lösung:**
```javascript
// Token Ablaufdatum prüfen
function isTokenExpired(token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return payload.exp * 1000 < Date.now();
}

if (isTokenExpired(accessToken)) {
  // Token erneuern
  const newToken = await refreshAccessToken();
}
```

---

## 📚 Weitere Ressourcen

- [API_REFERENCE.md](API_REFERENCE.md) - Komplette API-Dokumentation
- [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) - Permissions-System
- [FRONTEND_PERMISSIONS.md](FRONTEND_PERMISSIONS.md) - Frontend-Integration
- [QUICK_START.md](QUICK_START.md) - Schnelleinstieg

---

## 💡 Zusammenfassung

**Was du brauchst:**
1. ✅ Website ID (vom Admin-Panel)
2. ✅ API Key `pk_...` (für Frontend)
3. ✅ API Secret `sk_...` (nur für Backend)
4. ✅ Allowed Origins konfigurieren

**Frontend:**
```javascript
X-API-Key: pk_abc123...
Authorization: Bearer <access_token>
```

**Backend:**
```javascript
X-API-Secret: sk_xyz987...
```

**Sicherheit:**
- 🔒 API Secret NIEMALS im Frontend
- 🔒 Secrets in .env Datei
- 🔒 HTTPS in Production
- 🔒 CORS korrekt konfigurieren
