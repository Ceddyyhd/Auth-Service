# 🔑 Website-Credentials Übersicht

## Was du für die Integration brauchst

Wenn du eine Website im Auth Service registrierst, bekommst du automatisch diese Credentials:

### 1. **Website-ID** (UUID)
```
Beispiel: 550e8400-e29b-41d4-a716-446655440000
```
- **Verwendung:** Bei allen API-Anfragen als `website_id`
- **Sichtbar:** Ja
- **Speichern in:** Frontend + Backend Konfiguration

---

### 2. **API Key** (`pk_...`)
```
Beispiel: pk_vJQ2x9K7nT5wRm3pLh8cY4dF1zAb6eG0qS2uVw9XjNm
```
- **Verwendung:** Client-seitige API-Anfragen (JavaScript im Browser)
- **Header:** `X-API-Key: pk_...`
- **Sichtbar:** Ja (darf im Frontend-Code stehen)
- **Speichern in:** Frontend Environment Variables

---

### 3. **API Secret** (`sk_...`)
```
Beispiel: sk_mP9wQ8xL7vK6nB5hT4jY3cR2dF1sA0zG9eW8uV7xN6m
```
- **Verwendung:** NUR Server-seitige Anfragen (Backend)
- **Header:** `X-API-Secret: sk_...`
- **Sichtbar:** ⚠️ NEIN! Streng geheim
- **Speichern in:** Backend .env Datei (NIEMALS in Git!)

---

### 4. **Client ID** (OAuth2)
```
Beispiel: web_550e8400e29b41d4a716446655440000
```
- **Verwendung:** OAuth2-Flow (optional)
- **Sichtbar:** Ja

---

### 5. **Client Secret** (OAuth2)
```
Beispiel: secret_abc123def456ghi789
```
- **Verwendung:** OAuth2-Flow (optional)
- **Sichtbar:** ⚠️ NEIN! Geheim

---

## 🚀 Quick Setup

### Website im Admin-Panel erstellen

1. Gehe zu `http://localhost:8000/admin/`
2. Navigiere zu **Websites** → **Website hinzufügen**
3. Fülle die Felder aus:
   ```
   Name: Meine Website
   Domain: example.com
   Callback URL: https://example.com/auth/callback
   Allowed Origins: ["https://example.com", "http://localhost:3000"]
   ```
4. Nach dem Speichern werden automatisch generiert:
   - ✅ API Key (`pk_...`)
   - ✅ API Secret (`sk_...`)
   - ✅ Client ID
   - ✅ Client Secret

### ⚠️ WICHTIG:
**Kopiere sofort das API Secret!** Es wird später aus Sicherheitsgründen verschleiert angezeigt.

---

## 💻 Frontend Setup (.env)

```env
# Frontend Environment Variables
VITE_AUTH_SERVICE_URL=http://localhost:8000
VITE_WEBSITE_ID=550e8400-e29b-41d4-a716-446655440000
VITE_API_KEY=pk_vJQ2x9K7nT5wRm3pLh8cY4dF1zAb6eG0qS2uVw9XjNm

# ⚠️ Hier KEIN API Secret!
```

**React/Vue/Angular:**
```javascript
// config.js
export const config = {
  authServiceUrl: import.meta.env.VITE_AUTH_SERVICE_URL,
  websiteId: import.meta.env.VITE_WEBSITE_ID,
  apiKey: import.meta.env.VITE_API_KEY,
};
```

---

## 🔧 Backend Setup (.env)

```env
# Backend Environment Variables (Node.js, Python, PHP, etc.)
AUTH_SERVICE_URL=http://localhost:8000
AUTH_WEBSITE_ID=550e8400-e29b-41d4-a716-446655440000
AUTH_API_SECRET=sk_mP9wQ8xL7vK6nB5hT4jY3cR2dF1sA0zG9eW8uV7xN6m

# ⚠️ Diese Datei MUSS in .gitignore!
```

**.gitignore:**
```
.env
.env.local
.env.production
```

---

## 📝 Verwendungsbeispiele

### Frontend (JavaScript)

```javascript
// API-Anfrage mit API Key
const response = await fetch(`${AUTH_SERVICE_URL}/api/accounts/register/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,  // pk_...
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!',
    website_id: WEBSITE_ID,
  })
});
```

### Backend (Node.js)

```javascript
// Token-Verifizierung mit API Secret
const axios = require('axios');

async function verifyToken(token) {
  const response = await axios.post(
    `${process.env.AUTH_SERVICE_URL}/api/auth/verify-token/`,
    {
      token: token,
      website_id: process.env.AUTH_WEBSITE_ID,
    },
    {
      headers: {
        'X-API-Secret': process.env.AUTH_API_SECRET,  // sk_...
      }
    }
  );
  
  return response.data;
}
```

### Backend (Python/Django)

```python
import os
import requests

AUTH_API_SECRET = os.getenv('AUTH_API_SECRET')

def verify_token(token):
    response = requests.post(
        f'{os.getenv("AUTH_SERVICE_URL")}/api/auth/verify-token/',
        json={
            'token': token,
            'website_id': os.getenv('AUTH_WEBSITE_ID'),
        },
        headers={
            'X-API-Secret': AUTH_API_SECRET,  # sk_...
        }
    )
    return response.json()
```

---

## 🔐 Sicherheits-Checkliste

### ✅ Mache das:

- [x] API Key (`pk_`) im Frontend verwenden
- [x] API Secret (`sk_`) NUR im Backend
- [x] Secrets in .env Dateien speichern
- [x] .env zur .gitignore hinzufügen
- [x] HTTPS in Production verwenden
- [x] Allowed Origins korrekt konfigurieren
- [x] CORS-Header prüfen

### ❌ Mache das NICHT:

- [ ] API Secret im Frontend-Code
- [ ] Secrets in Git committen
- [ ] Secrets in Logs ausgeben
- [ ] HTTP in Production (immer HTTPS!)
- [ ] Secrets hardcoden

---

## 🆘 Credentials verloren?

### API Keys neu generieren

**Option 1: Django Shell**
```python
python manage.py shell

from accounts.models import Website

website = Website.objects.get(domain='example.com')
website.regenerate_api_keys()

print(f'Neuer API Key: {website.api_key}')
print(f'Neues API Secret: {website.api_secret}')
```

**Option 2: Admin-Panel**
1. Gehe zu Website-Details
2. Klicke auf "API Keys neu generieren"
3. Kopiere sofort die neuen Keys!

**⚠️ WICHTIG:** Nach Regenerierung:
- Alte Keys funktionieren nicht mehr
- Alle Websites mit alten Keys müssen aktualisiert werden
- Plane einen Wartungszeitraum!

---

## 📊 Credentials-Management

### Empfohlene Struktur

```
my-project/
├── frontend/
│   ├── .env                 # Website ID + API Key (pk_)
│   ├── .env.local          # Lokale Overrides
│   ├── .env.production     # Production Werte
│   └── .gitignore          # ⚠️ .env* hinzufügen!
│
├── backend/
│   ├── .env                # Website ID + API Secret (sk_)
│   ├── .env.local
│   ├── .env.production
│   └── .gitignore          # ⚠️ .env* hinzufügen!
│
└── docs/
    └── credentials.md      # Diese Datei (NICHT in Git!)
```

### Credential Rotation (Regelmäßig wechseln)

```bash
# Jeden Monat/Quartal neue Keys generieren:
python manage.py shell -c "
from accounts.models import Website
for website in Website.objects.all():
    old_key = website.api_key
    website.regenerate_api_keys()
    print(f'{website.name}:')
    print(f'  Alt: {old_key}')
    print(f'  Neu: {website.api_key}')
"
```

---

## 🧪 Testen

### Test-Credentials erstellen

```python
# test_setup.py
from accounts.models import Website

test_website = Website.objects.create(
    name='Test Website',
    domain='localhost:3000',
    callback_url='http://localhost:3000/auth/callback',
    allowed_origins=['http://localhost:3000', 'http://localhost:3001'],
    require_first_name=True,
    require_last_name=True,
)

print('=== TEST CREDENTIALS ===')
print(f'Website ID: {test_website.id}')
print(f'API Key: {test_website.api_key}')
print(f'API Secret: {test_website.api_secret}')
print(f'Client ID: {test_website.client_id}')
print(f'Client Secret: {test_website.client_secret}')
print('========================')
```

```bash
python manage.py shell < test_setup.py > test_credentials.txt
# ⚠️ Füge test_credentials.txt zu .gitignore hinzu!
```

---

## 📚 Weitere Infos

- [WEBSITE_INTEGRATION.md](WEBSITE_INTEGRATION.md) - Komplette Integrations-Anleitung
- [API_REFERENCE.md](API_REFERENCE.md) - API-Dokumentation
- [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) - Permissions-System

---

## 💡 Zusammenfassung

**Du brauchst:**

| Credential | Wo verwenden? | Öffentlich? | Beispiel |
|------------|---------------|-------------|----------|
| Website ID | Frontend + Backend | ✅ Ja | `550e8400-e29b...` |
| API Key | Frontend | ✅ Ja | `pk_vJQ2x9K7...` |
| API Secret | Backend | ❌ NEIN | `sk_mP9wQ8xL...` |
| Client ID | OAuth2 (optional) | ✅ Ja | `web_550e8400...` |
| Client Secret | OAuth2 (optional) | ❌ NEIN | `secret_abc123...` |

**Sichere Speicherung:**
- Frontend: `.env` mit `pk_` Keys
- Backend: `.env` mit `sk_` Keys
- Beide `.env` Dateien in `.gitignore`!
