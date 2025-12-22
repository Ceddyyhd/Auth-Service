# Auth Service - Zentrale Authentifizierung & Autorisierung

Ein sicherer, zentraler Authentifizierungs- und Autorisierungsservice mit Django, der OAuth2/OpenID Connect und JWT unterstützt. Ideal für die Integration in mehrere Websites mit einem einzigen Benutzerkonto.

## 🚀 Features

### 🔐 Authentifizierung
- **Single Sign-On (SSO)**: Ein Account für alle Websites
- **Email-basierte Registrierung** mit Verifikation
- **Social Login**: Google, Facebook, GitHub, Microsoft, Apple
- **OAuth2 & JWT**: Moderne Token-basierte Authentifizierung
- **Session Management**: Aktive Sessions pro Website verwalten

### 🎭 Berechtigungssystem (NEU & VEREINFACHT!)
- **Zentrale Verwaltung**: Alles im Benutzerprofil! 
- **Hierarchie**: Benutzer → Rollen → Berechtigungen
- **Global & Lokal**: Website-übergreifend oder website-spezifisch
- **Mehrfach-Rollen**: Ein Benutzer = mehrere Rollen möglich
- **Übersichtlich**: Icons und klare Struktur im Admin

📖 **Siehe:** [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) für komplette Anleitung

### 🌐 Multi-Website Support
- **Zentrale Benutzerverwaltung**: Ein Account, viele Websites
- **Website-spezifische Einstellungen**: Konfigurierbare Pflichtfelder
- **Flexible Rollenvergabe**: Verschiedene Rechte pro Website
- **API Credentials**: Eigene Client-ID/Secret pro Website

### 📝 Konfigurierbare Registrierung
- **Pflichtfelder pro Website**: Adresse, Telefon, Geburtsdatum, etc.
- **Profil-Vervollständigung**: Automatische Abfrage fehlender Daten
- **Social Login Integration**: Fehlende Daten nach Social Login ergänzen

📖 **Siehe:** [SOCIAL_LOGIN.md](SOCIAL_LOGIN.md) für Social Login Setup

## 📋 Anforderungen

- Python 3.9+
- PostgreSQL (empfohlen) oder SQLite (Entwicklung)
- Redis (für Caching und Sessions)

## 🛠️ Installation

### 1. Repository klonen

```bash
cd Auth-Service
```

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# oder
source venv/bin/activate  # Linux/Mac
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren

```bash
copy .env.example .env
```

Bearbeiten Sie `.env` und setzen Sie Ihre Konfiguration:

```env
SECRET_KEY=ihr-geheimer-schluessel
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Datenbank (PostgreSQL empfohlen für Produktion)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=auth_service
DB_USER=postgres
DB_PASSWORD=ihr-passwort
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=ihr-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS (Ihre Frontend URLs)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Datenbank migrieren

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Superuser erstellen

```bash
python manage.py createsuperuser
```

### 7. Server starten

```bash
python manage.py runserver
```

Der Service läuft jetzt auf: `http://localhost:8000`

## 📚 API Dokumentation

### Interaktive API-Dokumentation

Besuchen Sie nach dem Start des Servers:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **API Schema**: `http://localhost:8000/api/schema/`

### Hauptendpunkte

#### Authentication

```
POST   /api/accounts/register/          - Benutzer registrieren
POST   /api/accounts/login/             - Einloggen (JWT Tokens erhalten)
POST   /api/accounts/logout/            - Ausloggen
POST   /api/accounts/token/refresh/     - Access Token erneuern
GET    /api/accounts/profile/           - Profil abrufen
PUT    /api/accounts/profile/           - Profil aktualisieren
POST   /api/accounts/change-password/   - Passwort ändern
```

#### Website Management (Admin)

```
GET    /api/accounts/websites/          - Alle Websites auflisten
POST   /api/accounts/websites/          - Neue Website registrieren
GET    /api/accounts/websites/{id}/     - Website Details
PUT    /api/accounts/websites/{id}/     - Website aktualisieren
DELETE /api/accounts/websites/{id}/     - Website löschen
```

#### Access Control

```
POST   /api/accounts/verify-access/     - Website-Zugriff prüfen
GET    /api/accounts/sessions/          - Benutzersitzungen
```

#### Permissions & Roles

```
GET    /api/permissions/permissions/    - Berechtigungen auflisten
POST   /api/permissions/permissions/    - Berechtigung erstellen
GET    /api/permissions/roles/          - Rollen auflisten
POST   /api/permissions/roles/          - Rolle erstellen
POST   /api/permissions/assign-role/    - Rolle zuweisen
POST   /api/permissions/revoke-role/    - Rolle entziehen
GET    /api/permissions/check/me/       - Eigene Berechtigungen prüfen
POST   /api/permissions/check-permission/ - Spezifische Berechtigung prüfen
```

## 🔐 Integration in Ihre Website

### Beispiel: JavaScript/React Integration

#### 1. Benutzer registrieren

```javascript
async function register(email, username, password) {
  const response = await fetch('http://localhost:8000/api/accounts/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      username: username,
      password: password,
      password2: password,
    }),
  });
  
  const data = await response.json();
  
  // Tokens speichern
  localStorage.setItem('access_token', data.tokens.access);
  localStorage.setItem('refresh_token', data.tokens.refresh);
  
  return data;
}
```

#### 2. Benutzer einloggen

```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });
  
  const data = await response.json();
  
  // Tokens speichern
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}
```

#### 3. Geschützte Anfragen

```javascript
async function makeAuthenticatedRequest(url) {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (response.status === 401) {
    // Token abgelaufen, erneuern
    await refreshToken();
    return makeAuthenticatedRequest(url);
  }
  
  return response.json();
}
```

#### 4. Token erneuern

```javascript
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/api/accounts/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refreshToken,
    }),
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  
  return data;
}
```

#### 5. Website-Zugriff prüfen

```javascript
async function verifyWebsiteAccess(websiteId) {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/accounts/verify-access/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      website_id: websiteId,
    }),
  });
  
  const data = await response.json();
  return data.has_access;
}
```

#### 6. Berechtigungen prüfen

```javascript
async function checkPermission(permissionCodename, websiteId = null) {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/permissions/check-permission/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      permission_codename: permissionCodename,
      website_id: websiteId,
    }),
  });
  
  const data = await response.json();
  return data.has_permission;
}
```

### Beispiel: Python Integration

```python
import requests

class AuthServiceClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def login(self, email, password):
        """Benutzer einloggen"""
        response = requests.post(
            f'{self.base_url}/api/accounts/login/',
            json={'email': email, 'password': password}
        )
        data = response.json()
        self.access_token = data['access']
        self.refresh_token = data['refresh']
        return data
    
    def get_headers(self):
        """Authorization Header mit JWT Token"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def verify_access(self, website_id):
        """Website-Zugriff prüfen"""
        response = requests.post(
            f'{self.base_url}/api/accounts/verify-access/',
            json={'website_id': website_id},
            headers=self.get_headers()
        )
        return response.json()
    
    def check_permission(self, permission_codename, website_id=None):
        """Spezifische Berechtigung prüfen"""
        data = {'permission_codename': permission_codename}
        if website_id:
            data['website_id'] = website_id
        
        response = requests.post(
            f'{self.base_url}/api/permissions/check-permission/',
            json=data,
            headers=self.get_headers()
        )
        return response.json()['has_permission']

# Verwendung
client = AuthServiceClient()
client.login('user@example.com', 'password')

# Zugriff prüfen
has_access = client.verify_access('website-uuid')

# Berechtigung prüfen
can_view_reports = client.check_permission('view_reports', 'website-uuid')
```

## 🏗️ Architektur

### Datenbank-Schema

```
User (Custom User Model)
├── Website (M2M) - Erlaubte Websites
├── UserRole - Rollenzuweisungen
└── UserPermission - Direkte Berechtigungen

Website
├── Users (M2M)
├── Roles
├── Permissions
└── UserSessions

Role
├── Permissions (M2M)
└── Users (through UserRole)

Permission
└── Roles (M2M)
```

### Berechtigungssystem

**Globale Berechtigungen**: Gelten über alle Websites
- Beispiel: `manage_users`, `view_analytics`

**Lokale Berechtigungen**: Gelten nur für eine spezifische Website
- Beispiel: `edit_blog_posts` (nur für Website A)

**Rollen**: Gruppieren mehrere Berechtigungen
- Global: `Super Admin`, `Support`
- Lokal: `Website Admin`, `Content Editor`

**Priorität**: Direkte Berechtigungen > Rollen
- Explizite Verweigerungen überschreiben Rollenzuweisungen

## 🔒 Sicherheit

### Implementierte Sicherheitsmaßnahmen

✅ **Password Hashing**: Django's PBKDF2-SHA256
✅ **JWT Tokens**: Sichere Token-basierte Authentifizierung
✅ **Token Blacklisting**: Logout invalidiert Tokens
✅ **CORS Protection**: Konfigurierbare CORS-Regeln
✅ **CSRF Protection**: Django CSRF Middleware
✅ **XSS Protection**: Content Security Headers
✅ **Rate Limiting**: Kann über Redis implementiert werden
✅ **Session Tracking**: IP & User Agent Tracking

### Produktions-Empfehlungen

1. **HTTPS erzwingen**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Secret Keys sicher aufbewahren**
   - Verwenden Sie starke, zufällige Keys
   - Niemals in Git committen

3. **PostgreSQL verwenden**
   - SQLite nur für Entwicklung

4. **Redis konfigurieren**
   - Für Sessions und Caching

5. **Rate Limiting**
   - Implementieren Sie API Rate Limiting

## 🧪 Testing

```bash
# Tests ausführen
python manage.py test

# Mit Coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Deployment

### Mit Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "auth_service.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Mit Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_service
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    
  web:
    build: .
    command: gunicorn auth_service.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

## 🤝 Support & Beitrag

Bei Fragen oder Problemen:
1. Überprüfen Sie die API-Dokumentation
2. Prüfen Sie die Logs
3. Erstellen Sie ein Issue

## 📄 Lizenz

Dieses Projekt ist für die Verwendung in PalmDynamicX-Projekten vorgesehen.

## 🎯 Nächste Schritte

1. ✅ Basis-Setup abgeschlossen
2. 🔄 Website registrieren im Admin
3. 🔄 Berechtigungen und Rollen definieren
4. 🔄 In Ihre Websites integrieren
5. 🔄 Testing & Deployment

---

**Entwickelt mit ❤️ für PalmDynamicX**
