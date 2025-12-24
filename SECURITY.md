# 🔒 Sicherheits-Dokumentation - Auth Service

Diese Dokumentation beschreibt alle Sicherheitsmaßnahmen und Best Practices für den Auth Service.

## 📋 Inhaltsverzeichnis

- [Verschlüsselung & Transport](#verschlüsselung--transport)
- [Passwort-Sicherheit](#passwort-sicherheit)
- [JWT-Token-Sicherheit](#jwt-token-sicherheit)
- [HTTPS-Konfiguration](#https-konfiguration)
- [CORS & Origin-Validierung](#cors--origin-validierung)
- [Rate Limiting](#rate-limiting)
- [Session-Management](#session-management)
- [Datenbank-Sicherheit](#datenbank-sicherheit)
- [Sicherheits-Checkliste](#sicherheits-checkliste)

---

## 🔐 Verschlüsselung & Transport

### HTTPS ist PFLICHT in Produktion

**Alle API-Anfragen müssen über HTTPS erfolgen!**

```python
# settings.py - Produktion
DEBUG = False
SECURE_SSL_REDIRECT = True  # Erzwingt HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Was wird verschlüsselt?

✅ **Übertragung (Transport Layer):**
- Alle HTTP-Requests über TLS 1.2 oder höher
- JWT-Tokens werden nur über HTTPS übertragen
- Passwörter werden nur über HTTPS gesendet

✅ **Speicherung (Storage Layer):**
- Passwörter: bcrypt mit Salt (12 Rounds)
- Sensible Daten: AES-256 Verschlüsselung (falls konfiguriert)
- Datenbank: Verschlüsselung at rest

❌ **NICHT verschlüsselt:**
- Öffentliche Daten (Benutzername, nicht-sensible Profilfelder)
- JWT-Tokens selbst (aber signiert!)

### Nginx HTTPS-Konfiguration:

```nginx
server {
    listen 443 ssl http2;
    server_name api.ihredomain.com;
    
    # SSL Zertifikate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.ihredomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.ihredomain.com/privkey.pem;
    
    # SSL-Protokolle (Nur sichere)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS Header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Weitere Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP zu HTTPS Redirect
server {
    listen 80;
    server_name api.ihredomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🔑 Passwort-Sicherheit

### Hashing-Algorithmus: bcrypt

```python
# Django verwendet automatisch bcrypt
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Bcrypt',  # Primär
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]

# Beispiel Hash:
# bcrypt$12$rounds$salt$hashedpassword...
```

### Passwort-Anforderungen:

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

**Anforderungen:**
- ✅ Mindestens 8 Zeichen
- ✅ Keine häufig verwendeten Passwörter
- ✅ Nicht nur Zahlen
- ✅ Empfohlen: Groß-/Kleinbuchstaben + Zahlen + Sonderzeichen

### Passwort-Reset-Prozess:

```
1. Benutzer fordert Reset an
   ↓
2. Token generiert (SHA-256, 32 bytes)
   ↓
3. Token-Hash in DB gespeichert (NICHT Klartext!)
   ↓
4. E-Mail mit Link gesendet (Token im Link)
   ↓
5. Token läuft nach 1 Stunde ab
   ↓
6. Neues Passwort wird gesetzt
   ↓
7. Token wird invalidiert
```

**⚠️ Wichtig:**
- Tokens werden NIEMALS im Klartext in der DB gespeichert
- Tokens sind nur 1 Stunde gültig
- Nach Verwendung werden Tokens sofort gelöscht
- Rate Limiting: Max 3 Reset-Anfragen pro Stunde

---

## 🎫 JWT-Token-Sicherheit

### Token-Struktur

```
JWT = Header.Payload.Signature

Header:     { "typ": "JWT", "alg": "HS256" }
Payload:    { "user_id": "...", "exp": 1234567890 }
Signature:  HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

### Token-Arten:

| Token | Gültigkeitsdauer | Verwendung | Speicherort |
|-------|------------------|------------|-------------|
| Access Token | 15 Minuten | API-Zugriff | localStorage/sessionStorage |
| Refresh Token | 7 Tage | Token erneuern | localStorage (httpOnly Cookie bevorzugt) |

### Sicherheitsmerkmale:

✅ **Signiert:** Tokens können nicht gefälscht werden  
✅ **Zeitlich begrenzt:** Automatischer Ablauf  
✅ **User-gebunden:** Enthält User-ID  
✅ **Revoke-fähig:** Kann serverseitig ungültig gemacht werden  

### Secret Key Sicherheit:

```python
# .env - NIEMALS in Git committen!
SECRET_KEY=ihr-sehr-langes-zufälliges-geheimnis-hier-mindestens-50-zeichen-lang

# Generieren eines sicheren Keys:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**⚠️ KRITISCH:**
- Secret Key NIEMALS in Git committen
- Secret Key NIEMALS im Client-Code
- Secret Key mindestens 50 Zeichen lang
- Secret Key regelmäßig rotieren (alle 3-6 Monate)

### Token-Speicherung im Frontend:

```javascript
// ❌ UNSICHER - Nicht verwenden!
// Token in URL
window.location.href = '/dashboard?token=' + accessToken;

// Token in Cookie ohne httpOnly
document.cookie = `token=${accessToken}`;

// ✅ SICHER - Verwenden!
// Option 1: localStorage (einfach, XSS-Risiko)
localStorage.setItem('access_token', accessToken);

// Option 2: sessionStorage (sicherer, nur aktuelle Session)
sessionStorage.setItem('access_token', accessToken);

// Option 3: httpOnly Cookie (am sichersten, Backend setzt Cookie)
// Backend:
response.set_cookie(
    'access_token',
    access_token,
    httponly=True,  # JavaScript kann nicht zugreifen
    secure=True,    # Nur über HTTPS
    samesite='Strict'  # CSRF-Schutz
)
```

### Token-Refresh-Flow:

```javascript
async function refreshAccessToken() {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('https://api.ihredomain.com/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (!response.ok) {
      // Refresh fehlgeschlagen - Logout
      logout();
      return null;
    }
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    
    return data.access;
  } catch (error) {
    console.error('Token refresh failed:', error);
    logout();
    return null;
  }
}

// Automatischer Refresh bei 401
async function authenticatedFetch(url, options) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  if (response.status === 401) {
    // Token abgelaufen - erneuern
    const newToken = await refreshAccessToken();
    
    if (newToken) {
      // Retry mit neuem Token
      response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        }
      });
    }
  }
  
  return response;
}
```

---

## 🌐 HTTPS-Konfiguration

### Let's Encrypt SSL-Zertifikat (kostenlos):

```bash
# Certbot installieren
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Zertifikat generieren
sudo certbot --nginx -d api.ihredomain.com

# Auto-Renewal (alle 90 Tage)
sudo certbot renew --dry-run

# Cron-Job für Auto-Renewal
0 12 * * * /usr/bin/certbot renew --quiet
```

### Django HTTPS-Einstellungen:

```python
# settings.py
SECURE_SSL_REDIRECT = True  # HTTP → HTTPS Redirect
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie-Sicherheit
SESSION_COOKIE_SECURE = True  # Nur über HTTPS
SESSION_COOKIE_HTTPONLY = True  # Kein JavaScript-Zugriff
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF-Schutz

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Content-Type-Sniffing verhindern
SECURE_CONTENT_TYPE_NOSNIFF = True

# X-Frame-Options (Clickjacking-Schutz)
X_FRAME_OPTIONS = 'DENY'
```

---

## 🚧 CORS & Origin-Validierung

### CORS-Konfiguration:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'https://www.ihredomain.com',
    'https://app.ihredomain.com',
    # NUR registrierte und vertrauenswürdige Origins!
]

# ❌ NIEMALS in Produktion:
# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True  # Für httpOnly Cookies

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]
```

### Website-basierte Origin-Validierung:

```python
# Website-Model
class Website(models.Model):
    allowed_origins = models.JSONField(default=list)
    
# Validation
def validate_origin(request, website_id):
    origin = request.META.get('HTTP_ORIGIN')
    website = Website.objects.get(id=website_id)
    
    if origin not in website.allowed_origins:
        raise PermissionDenied('Origin not allowed')
```

---

## ⏱️ Rate Limiting

### Schutz vor Brute-Force-Angriffen:

```python
# settings.py - django-ratelimit
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Views mit Rate Limiting:
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Max 5 Login-Versuche pro Minute pro IP
    pass

@ratelimit(key='ip', rate='3/h', method='POST')
def password_reset_view(request):
    # Max 3 Passwort-Resets pro Stunde pro IP
    pass

@ratelimit(key='user', rate='100/h', method='GET')
def api_view(request):
    # Max 100 Requests pro Stunde pro User
    pass
```

### Nginx Rate Limiting:

```nginx
# /etc/nginx/nginx.conf
http {
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    
    server {
        location /api/accounts/login/ {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://localhost:8000;
        }
        
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://localhost:8000;
        }
    }
}
```

---

## 📊 Session-Management

### Session-Sicherheit:

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # DB-basiert
SESSION_COOKIE_AGE = 86400  # 24 Stunden
SESSION_SAVE_EVERY_REQUEST = True  # Erneuert Session bei jedem Request
SESSION_COOKIE_SECURE = True  # Nur über HTTPS
SESSION_COOKIE_HTTPONLY = True  # Kein JavaScript-Zugriff
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF-Schutz
```

### Session-Tracking:

```python
# models.py
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
```

**Features:**
- ✅ Mehrere aktive Sessions pro Benutzer
- ✅ IP-Adresse und User-Agent tracking
- ✅ Session-Übersicht für Benutzer
- ✅ "Alle Geräte abmelden"-Funktion
- ✅ Verdächtige Login-Benachrichtigungen

---

## 🗄️ Datenbank-Sicherheit

### PostgreSQL Sicherheit:

```sql
-- Dedicated User mit minimalen Rechten
CREATE USER auth_service WITH PASSWORD 'sicheres-passwort';
CREATE DATABASE auth_service_db OWNER auth_service;

-- Nur notwendige Rechte
GRANT CONNECT ON DATABASE auth_service_db TO auth_service;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO auth_service;

-- SSL-Verbindung erzwingen
ALTER USER auth_service WITH CONNECTION LIMIT 10;
```

### Django Datenbank-Konfiguration:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_service_db',
        'USER': 'auth_service',
        'PASSWORD': os.getenv('DB_PASSWORD'),  # Aus .env!
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',  # SSL erzwingen
        },
        'CONN_MAX_AGE': 600,  # Connection Pooling
    }
}
```

### Encryption at Rest:

```bash
# PostgreSQL Datenbank-Verschlüsselung
# /etc/postgresql/14/main/postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

---

## ✅ Sicherheits-Checkliste

### Vor Produktions-Deployment:

#### Django-Einstellungen:
- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` aus Umgebungsvariable (nicht hardcoded)
- [ ] `ALLOWED_HOSTS` korrekt konfiguriert
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`
- [ ] `X_FRAME_OPTIONS = 'DENY'`
- [ ] CORS nur für vertrauenswürdige Origins

#### Server-Konfiguration:
- [ ] HTTPS mit gültigem SSL-Zertifikat
- [ ] TLS 1.2 oder höher
- [ ] HTTP zu HTTPS Redirect
- [ ] Security Headers konfiguriert
- [ ] Rate Limiting aktiviert
- [ ] Firewall konfiguriert (nur Ports 80, 443 offen)

#### Datenbank:
- [ ] PostgreSQL statt SQLite
- [ ] Starkes DB-Passwort
- [ ] SSL-Verbindung zur DB
- [ ] Regelmäßige Backups
- [ ] Encryption at Rest aktiviert

#### Anwendung:
- [ ] Passwörter mit bcrypt gehasht
- [ ] JWT-Tokens mit sicherem Secret Key
- [ ] E-Mail-Verifizierung aktiviert
- [ ] MFA (2FA) angeboten
- [ ] Session-Management aktiv
- [ ] Logging konfiguriert

#### Monitoring:
- [ ] Error-Tracking (z.B. Sentry)
- [ ] Security-Monitoring
- [ ] Failed-Login-Alerts
- [ ] Ungewöhnliche Aktivitäten überwachen

#### Code:
- [ ] Keine Secrets im Code
- [ ] Keine Debug-Statements
- [ ] Input-Validierung überall
- [ ] SQL-Injection-Schutz (Django ORM)
- [ ] XSS-Schutz aktiv

### Regelmäßige Wartung:

- [ ] Dependencies aktualisieren (monatlich)
- [ ] Security-Patches einspielen (sofort)
- [ ] SSL-Zertifikate erneuern (vor Ablauf)
- [ ] Secret Key rotieren (alle 6 Monate)
- [ ] Logs überprüfen (täglich)
- [ ] Backups testen (monatlich)
- [ ] Penetration Tests (jährlich)

---

## 🚨 Incident Response

### Bei Sicherheitsvorfall:

1. **Sofort:**
   - Betroffene Systeme isolieren
   - Alle Sessions invalidieren
   - Secret Keys rotieren
   - Betroffene Benutzer benachrichtigen

2. **Analyse:**
   - Logs überprüfen
   - Umfang ermitteln
   - Einfallsvektor identifizieren

3. **Behebung:**
   - Sicherheitslücke schließen
   - Patches einspielen
   - Systeme wiederherstellen

4. **Nachbereitung:**
   - Post-Mortem-Analyse
   - Prozesse verbessern
   - Monitoring erweitern

---

## 📚 Weitere Ressourcen

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Bei Sicherheitsfragen oder Vorfällen:** security@ihredomain.com

**Letzte Aktualisierung:** 24.12.2025
