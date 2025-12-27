# API-Key Authentifizierung

## Übersicht

Das Auth-Service erfordert jetzt für **alle API-Anfragen** einen gültigen API-Key. Dies verhindert, dass nicht autorisierte Clients API-Anfragen senden können.

## API-Keys erhalten

API-Keys sind mit Websites verknüpft. Jede Website, die das Auth-Service nutzt, erhält automatisch:
- **API-Key**: Öffentlicher Key für die Identifizierung
- **API-Secret**: Geheimer Key für zusätzliche Sicherheit (optional)

### API-Keys im Admin-Panel verwalten

1. Melden Sie sich im Django Admin an: `http://localhost:8000/admin/`
2. Navigieren Sie zu **Accounts > Websites**
3. Wählen Sie Ihre Website aus oder erstellen Sie eine neue
4. Die API-Keys werden automatisch generiert und angezeigt

### Programmatisch API-Keys generieren

Sie können auch das Python-Script verwenden:
```bash
python generate_api_keys.py
```

## API-Key in Anfragen verwenden

### HTTP-Header

Fügen Sie den API-Key zu jeder API-Anfrage als Header hinzu:

```
X-API-Key: ihr_api_key_hier
```

Optional (für erhöhte Sicherheit):
```
X-API-Key: ihr_api_key_hier
X-API-Secret: ihr_api_secret_hier
```

### JavaScript Beispiel

```javascript
// Registrierung
async function register(userData) {
  const response = await fetch('http://localhost:8000/api/accounts/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY_HERE'
    },
    body: JSON.stringify(userData)
  });
  
  return await response.json();
}

// Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY_HERE'
    },
    body: JSON.stringify({
      username: email,
      password: password
    })
  });
  
  return await response.json();
}

// Profil abrufen (mit JWT-Token UND API-Key)
async function getProfile(accessToken) {
  const response = await fetch('http://localhost:8000/api/accounts/profile/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'X-API-Key': 'YOUR_API_KEY_HERE'
    }
  });
  
  return await response.json();
}
```

### Python Beispiel

```python
import requests

API_KEY = 'your_api_key_here'
API_SECRET = 'your_api_secret_here'  # Optional
BASE_URL = 'http://localhost:8000/api/accounts'

# Headers für alle Anfragen
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    # 'X-API-Secret': API_SECRET  # Optional für erhöhte Sicherheit
}

# Registrierung
def register(email, username, password, website_id):
    data = {
        'email': email,
        'username': username,
        'password': password,
        'password_confirm': password,
        'website_id': website_id
    }
    
    response = requests.post(
        f'{BASE_URL}/register/',
        json=data,
        headers=headers
    )
    
    return response.json()

# Login
def login(email, password):
    data = {
        'username': email,
        'password': password
    }
    
    response = requests.post(
        f'{BASE_URL}/login/',
        json=data,
        headers=headers
    )
    
    return response.json()

# Profil abrufen
def get_profile(access_token):
    profile_headers = headers.copy()
    profile_headers['Authorization'] = f'Bearer {access_token}'
    
    response = requests.get(
        f'{BASE_URL}/profile/',
        headers=profile_headers
    )
    
    return response.json()
```

### cURL Beispiel

```bash
# Registrierung
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "website_id": "your-website-uuid"
  }'

# Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePass123!"
  }'

# Profil abrufen
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

## Authentifizierungsstrategien

Das System unterstützt verschiedene Authentifizierungsstrategien je nach Endpoint:

### 1. Nur API-Key erforderlich
Diese Endpoints benötigen nur einen API-Key (keine Benutzer-Authentifizierung):
- `POST /api/accounts/register/` - Benutzerregistrierung
- `POST /api/accounts/login/` - Benutzer-Login
- `POST /api/accounts/resend-verification/` - Verifizierungs-E-Mail erneut senden
- `POST /api/accounts/verify-email/` - E-Mail verifizieren
- `POST /api/accounts/request-password-reset/` - Passwort-Reset anfordern
- `POST /api/accounts/reset-password/` - Passwort zurücksetzen
- Alle SSO-Endpoints
- Alle Social-Login-Endpoints

### 2. API-Key ODER JWT-Token
Diese Endpoints akzeptieren entweder einen API-Key ODER einen JWT-Token:
- `POST /api/accounts/logout/` - Benutzer-Logout
- `GET/PUT/PATCH /api/accounts/profile/` - Profil anzeigen/bearbeiten
- `POST /api/accounts/change-password/` - Passwort ändern
- `POST /api/accounts/verify-access/` - Zugriff verifizieren
- `GET /api/accounts/sessions/` - Sessions auflisten
- Alle MFA-Endpoints

### 3. Admin ODER API-Key
Diese Endpoints erfordern entweder Admin-Rechte ODER einen API-Key:
- `GET/POST /api/accounts/websites/` - Websites auflisten/erstellen
- `GET/PUT/DELETE /api/accounts/websites/{id}/` - Website-Details
- `POST/DELETE /api/accounts/users/{user_id}/websites/` - Website-Zugriff verwalten

## Fehlerbehandlung

### Fehlender API-Key
**Status Code:** 403 Forbidden
```json
{
  "detail": "API-Key fehlt. Bitte fügen Sie den X-API-Key Header zu Ihrer Anfrage hinzu."
}
```

### Ungültiger API-Key
**Status Code:** 403 Forbidden
```json
{
  "detail": "API-Key ist ungültig oder die zugehörige Website ist nicht aktiv."
}
```

### Ungültiger API-Secret
**Status Code:** 403 Forbidden
```json
{
  "detail": "API-Secret ist ungültig."
}
```

## Sicherheitshinweise

1. **API-Keys geheim halten**: Speichern Sie API-Keys niemals in öffentlichen Repositories oder Client-Side-Code
2. **Umgebungsvariablen verwenden**: Speichern Sie API-Keys in Umgebungsvariablen oder sicheren Konfigurationsdateien
3. **HTTPS verwenden**: Übertragen Sie API-Keys nur über HTTPS-Verbindungen
4. **API-Secret nutzen**: Für erhöhte Sicherheit sollten Sie auch den API-Secret Header verwenden
5. **Keys rotieren**: Ändern Sie regelmäßig Ihre API-Keys, besonders nach Sicherheitsvorfällen

## Migration bestehender Clients

Falls Sie bereits bestehende Clients haben, die das Auth-Service nutzen:

1. **API-Keys abrufen**: Holen Sie sich die API-Keys für Ihre Website aus dem Admin-Panel
2. **Code aktualisieren**: Fügen Sie den `X-API-Key` Header zu allen API-Anfragen hinzu
3. **Testen**: Testen Sie alle Endpoints gründlich
4. **Deployment**: Rollen Sie die Änderungen aus

### Beispiel Migration (JavaScript)

**Vorher:**
```javascript
fetch('http://localhost:8000/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(userData)
})
```

**Nachher:**
```javascript
fetch('http://localhost:8000/api/accounts/register/', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'X-API-Key': process.env.AUTH_API_KEY  // API-Key hinzugefügt
  },
  body: JSON.stringify(userData)
})
```

## Entwicklungsumgebung

Für lokale Entwicklung können Sie Ihre API-Keys in einer `.env` Datei speichern:

```env
AUTH_API_KEY=your_development_api_key
AUTH_API_SECRET=your_development_api_secret
```

Stellen Sie sicher, dass `.env` in Ihrer `.gitignore` Datei enthalten ist!

## Fragen und Support

Bei Fragen zur API-Key-Authentifizierung:
1. Überprüfen Sie diese Dokumentation
2. Kontaktieren Sie das Entwicklerteam
3. Prüfen Sie die Django-Logs für detaillierte Fehlermeldungen
