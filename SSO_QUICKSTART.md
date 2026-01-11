# 🔐 SSO (Single Sign-On) - Komplette Anleitung

## 📖 Was ist SSO?

Single Sign-On (SSO) ermöglicht es Benutzern, sich **einmal** anzumelden und automatisch auf **allen verbundenen Websites** eingeloggt zu sein - ohne erneute Eingabe von Benutzername und Passwort.

### Beispiel-Szenario
1. **Benutzer** ist auf **Website A** (z.B. `palmservers.de`) angemeldet
2. **Benutzer** klickt auf einen Link zu **Website B** (z.B. `auth.palmdynamicx.de`)
3. **Website B** erkennt automatisch den Benutzer und meldet ihn an
4. **Benutzer** ist sofort eingeloggt - **keine erneute Anmeldung nötig!** ✨

### 🌐 Cross-Domain SSO

**Wichtig:** SSO funktioniert auch **über verschiedene Domains** hinweg!

- ✅ `palmservers.de` → `auth.palmdynamicx.de`
- ✅ `shop.example.com` → `blog.different-domain.com`
- ✅ Jede Domain zu jeder anderen Domain

**Challenge:** Session Cookies funktionieren nur innerhalb derselben Domain. Für Cross-Domain SSO verwenden wir einen speziellen Flow mit **SSO-Token-Austausch** über Redirects.

---

## 🎯 Wie funktioniert der SSO-Flow?

### Cross-Domain SSO Flow (z.B. palmservers.de → auth.palmdynamicx.de)

```
┌─────────────────┐       ┌──────────────┐       ┌─────────────────┐
│  palmservers.de │       │ Auth-Service │       │auth.palmdynamicx│
│   (Website A)   │       │  (Zentral)   │       │   (Website B)   │
└────────┬────────┘       └──────┬───────┘       └────────┬────────┘
       │                         │                          │
       │ 1. Benutzer angemeldet  │                          │
       │    (hat Session)        │                          │
       │                         │                          │
       │ 2. Klick auf Link       │                          │
       │    zu Website B         │                          │
       ├─────────────────────────┼─────────────────────────→│
       │                         │                          │
       │                         │ 3. Website B prüft:      │
       │                         │    Hat User Session?     │
       │                         │    → NEIN                │
       │                         │                          │
       │                         │ 4. SSO initieren         │
       │                         │←─────────────────────────┤
       │                         │    POST /sso/initiate/   │
       │                         │    + API Key             │
       │                         │    + redirect_uri        │
       │                         │                          │
       │                         │ 5. Auth prüft Session    │
       │                         │    User ist angemeldet!  │
       │                         │    → Token generieren    │
       │                         │                          │
       │                         │ 6. SSO-Token zurück      │
       │                         │──────────────────────────→│
       │                         │    { sso_token: "..." }  │
       │                         │                          │
       │                         │ 7. Token gegen JWT       │
       │                         │    austauschen           │
       │                         │←─────────────────────────┤
       │                         │    POST /sso/callback/   │
       │                         │    + sso_token           │
       │                         │                          │
       │                         │ 8. JWT Tokens zurück     │
       │                         │──────────────────────────→│
       │                         │    { access, refresh }   │
       │                         │                          │
       │                         │                          │ 9. User eingeloggt!
       │                         │                          │    ✅ Automatisch
       │                         │                          │       angemeldet
```

---

## 🚀 Implementation Guide

### Voraussetzungen

1. ✅ **Website muss registriert sein** im Auth-Service
2. ✅ **API Key** für die Website vorhanden
3. ✅ **Erlaubte Origins** konfiguriert
4. ✅ **Session Management** auf beiden Websites

---

## 📝 Schritt-für-Schritt Integration

## 🌐 Cross-Domain SSO: Wichtige Unterschiede

### Problem: Session Cookies funktionieren nicht über verschiedene Domains

Wenn User auf `palmservers.de` angemeldet ist, hat er ein Session Cookie für `palmservers.de`. Dieses Cookie wird **nicht automatisch** an `auth.palmdynamicx.de` gesendet (aus Sicherheitsgründen).

### Lösung: SSO-Check Endpoint

Für Cross-Domain SSO gibt es **zwei Ansätze**:

#### **Ansatz 1: Silent Auth via Popup/iframe** (Empfohlen)
```javascript
// Website B prüft SSO-Status beim Auth-Service
async function checkSSOStatus() {
    const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/status/', {
        method: 'POST',
        credentials: 'include', // Wichtig für Cross-Domain Cookies!
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'your-api-key'
        },
        body: JSON.stringify({
            website_id: 'your-website-id'
        })
    });
    
    const data = await response.json();
    
    if (data.sso_available && data.authenticated) {
        // User hat aktive Session beim Auth-Service!
        // Jetzt SSO Token anfordern
        await initiateSSOLogin();
    } else {
        // Normaler Login-Flow
        showLoginForm();
    }
}
```

#### **Ansatz 2: Direkter Redirect** (Einfacher)
```javascript
// User klickt auf "Mit SSO anmelden"
function loginWithSSO() {
    const AUTH_SERVICE = 'https://auth.palmdynamicx.de';
    const CALLBACK_URL = encodeURIComponent(window.location.origin + '/auth/sso-callback');
    const WEBSITE_ID = 'your-website-id';
    
    // Redirect direkt zum Auth-Service
    // Der Auth-Service prüft Session und leitet zurück
    window.location.href = `${AUTH_SERVICE}/api/accounts/sso/initiate/?website_id=${WEBSITE_ID}&redirect_uri=${CALLBACK_URL}`;
}
```

---

### **Schritt 1: SSO-Button auf Website A erstellen**

Auf der **Quell-Website** (z.B. `palmservers.de` - wo der User bereits eingeloggt ist):

```html
<!-- SSO Login Button für Cross-Domain -->
<button onclick="loginWithSSO()">
    🔐 Zu auth.palmdynamicx.de mit Auto-Login
</button>

<script>
async function loginWithSSO() {
    const WEBSITE_B_ID = '8bc78e67-b249-4e86-b44a-ace71b9a868a';
    const AUTH_SERVICE = 'https://auth.palmdynamicx.de';
    const WEBSITE_B_CALLBACK = 'https://auth.palmdynamicx.de/auth/sso-callback';
    
    // Redirect zu Auth-Service SSO Initiate
    const ssoUrl = `${AUTH_SERVICE}/api/accounts/sso/initiate/`;
    
    // Redirect mit POST (weil wir API Key brauchen)
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = ssoUrl;
    
    const websiteInput = document.createElement('input');
    websiteInput.type = 'hidden';
    websiteInput.name = 'website_id';
    websiteInput.value = WEBSITE_B_ID;
    
    const redirectInput = document.createElement('input');
    redirectInput.type = 'hidden';
    redirectInput.name = 'redirect_uri';
    redirectInput.value = WEBSITE_B_CALLBACK;
    
    form.appendChild(websiteInput);
    form.appendChild(redirectInput);
    document.body.appendChild(form);
    form.submit();
}
</script>
```

### **Alternative: Backend-basierter SSO-Flow**

Besser und sicherer ist es, SSO über das Backend zu initiieren:

```javascript
// Frontend (Website A)
async function loginWithSSO() {
    try {
        // Rufe Backend auf, um SSO zu initiieren
        const response = await fetch('/api/sso/initiate-to-website-b', {
            method: 'POST',
            credentials: 'include', // Session Cookie mitsenden
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.redirect_url) {
            // Redirect zu Website B mit SSO Token
            window.location.href = data.redirect_url;
        }
    } catch (error) {
        console.error('SSO failed:', error);
        alert('SSO-Anmeldung fehlgeschlagen');
    }
}
```

```python
# Backend (Website A) - z.B. in views.py
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def initiate_sso_to_website_b(request):
    """Initiiert SSO zu Website B"""
    
    AUTH_SERVICE = 'https://auth.palmdynamicx.de'
    WEBSITE_B_ID = '8bc78e67-b249-4e86-b44a-ace71b9a868a'
    WEBSITE_B_CALLBACK = 'https://website-b.com/auth/sso-callback'
    API_KEY = 'your-api-key-here'
    
    # Session Cookie vom User holen
    session_cookie = request.COOKIES.get('sessionid')
    
    if not session_cookie:
        return JsonResponse({
            'error': 'Not logged in'
        }, status=401)
    
    # SSO beim Auth-Service initiieren
    response = requests.post(
        f'{AUTH_SERVICE}/api/accounts/sso/initiate/',
        json={
            'website_id': WEBSITE_B_ID,
            'redirect_uri': WEBSITE_B_CALLBACK
        },
        headers={
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        cookies={
            'sessionid': session_cookie  # Session weiterleiten!
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({
            'error': 'SSO initiation failed',
            'details': response.text
        }, status=response.status_code)
```

---

### **Schritt 2: SSO Callback auf Website B erstellen**

Auf der **Ziel-Website** (Website B), wo der User automatisch eingeloggt werden soll:

```javascript
// Website B - sso-callback.html oder React Component

async function handleSSOCallback() {
    // SSO Token aus URL Parameter lesen
    const urlParams = new URLSearchParams(window.location.search);
    const ssoToken = urlParams.get('sso_token');
    
    if (!ssoToken) {
        console.error('No SSO token found');
        window.location.href = '/login'; // Fallback zu normaler Anmeldung
        return;
    }
    
    const AUTH_SERVICE = 'https://auth.palmdynamicx.de';
    const WEBSITE_B_ID = '8bc78e67-b249-4e86-b44a-ace71b9a868a';
    const API_KEY = 'your-website-b-api-key';
    
    try {
        // Token gegen JWT austauschen
        const response = await fetch(`${AUTH_SERVICE}/api/accounts/sso/callback/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                sso_token: ssoToken,
                website_id: WEBSITE_B_ID
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // JWT Tokens speichern
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // User Daten speichern (optional)
            localStorage.setItem('user', JSON.stringify(data.user));
            
            console.log('✅ SSO Login erfolgreich!');
            console.log('User:', data.user.email);
            
            // Redirect zur Dashboard oder Startseite
            window.location.href = '/dashboard';
            
        } else {
            const error = await response.json();
            console.error('SSO Callback failed:', error);
            window.location.href = '/login?error=sso_failed';
        }
        
    } catch (error) {
        console.error('SSO Error:', error);
        window.location.href = '/login?error=network_error';
    }
}

// Bei Seiten-Load ausführen
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleSSOCallback);
} else {
    handleSSOCallback();
}
```

---

### **Schritt 3: Backend SSO Callback (Empfohlen)**

Sicherer ist es, den Token-Austausch im Backend zu machen:

```python
# Website B - Backend (views.py)
import requests
from django.shortcuts import redirect
from django.http import JsonResponse

def sso_callback(request):
    """
    Callback Endpoint für SSO
    Tauscht SSO Token gegen JWT und erstellt Session
    """
    sso_token = request.GET.get('sso_token')
    
    if not sso_token:
        return redirect('/login?error=no_sso_token')
    
    AUTH_SERVICE = 'https://auth.palmdynamicx.de'
    WEBSITE_ID = '8bc78e67-b249-4e86-b44a-ace71b9a868a'
    API_KEY = 'your-api-key'
    
    try:
        # Token beim Auth-Service austauschen
        response = requests.post(
            f'{AUTH_SERVICE}/api/accounts/sso/callback/',
            json={
                'sso_token': sso_token,
                'website_id': WEBSITE_ID
            },
            headers={
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # JWT Tokens erhalten
            access_token = data['access']
            refresh_token = data['refresh']
            user_data = data['user']
            
            # Session für User erstellen
            # Option 1: JWT in HttpOnly Cookie speichern
            response = redirect('/dashboard')
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=3600  # 1 Stunde
            )
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=604800  # 7 Tage
            )
            
            return response
            
        else:
            print(f'SSO callback failed: {response.text}')
            return redirect('/login?error=sso_failed')
            
    except Exception as e:
        print(f'SSO error: {str(e)}')
        return redirect('/login?error=sso_error')
```

---

## 🔧 API Reference

### 1️⃣ **POST /api/accounts/sso/initiate/**

Startet den SSO-Prozess.

**Authentication:** API Key (im Header `X-API-Key`)

**Request Body:**
```json
{
  "website_id": "8bc78e67-b249-4e86-b44a-ace71b9a868a",
  "redirect_uri": "https://website-b.com/auth/sso-callback"
}
```

**Response (User eingeloggt):**
```json
{
  "authenticated": true,
  "sso_token": "abc123def456789...",
  "redirect_url": "https://website-b.com/auth/sso-callback?sso_token=abc123def456789...",
  "expires_in": 300
}
```

**Response (User NICHT eingeloggt):**
```json
{
  "authenticated": false,
  "login_url": "https://auth.palmdynamicx.de/login?website_id=...&return_url=...",
  "message": "User must login first"
}
```

**Wichtig:** 
- ⚠️ Das **Session Cookie** muss mitgesendet werden!
- ⚠️ Ohne Session Cookie erkennt der Auth-Service den User nicht als eingeloggt

---

### 2️⃣ **POST /api/accounts/sso/callback/**

Tauscht SSO Token gegen JWT Tokens.

**Authentication:** API Key (im Header `X-API-Key`)

**Request Body:**
```json
{
  "sso_token": "abc123def456789...",
  "website_id": "8bc78e67-b249-4e86-b44a-ace71b9a868a"
}
```

**Response (Erfolgreich):**
```json
{
  "success": true,
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "Max",
    "last_name": "Mustermann"
  }
}
```

**Error Responses:**
```json
// Token ungültig oder abgelaufen
{
  "error": "SSO token has expired or already been used"
}

// Token nicht gefunden
{
  "error": "Invalid SSO token"
}
```

---

## ⚠️ Häufige Fehler und Lösungen

### ❌ **Problem 1: 401 "token_not_valid"**

```json
{
  "detail": "Der Token ist für keinen Tokentyp gültig",
  "code": "token_not_valid"
}
```

**Ursache:** Du versuchst, SSO zu initiieren, sendest aber einen **JWT Access Token** statt einem **Session Cookie**.

**Lösung:**
- ✅ Verwende **Session-basierte Authentication**
- ✅ Sende das **Session Cookie** mit: `Cookie: sessionid=xyz123`
- ❌ Sende KEINEN JWT Bearer Token im Authorization Header

**Warum?** SSO funktioniert über Sessions, nicht über JWT. Der Auth-Service muss wissen, dass der User eine aktive Browser-Session hat.

---

### ❌ **Problem 2: "authenticated": false**

**Ursache:** Session Cookie fehlt oder ist ungültig.

**Lösung:**
```javascript
// Stelle sicher, dass Session Cookie mitgesendet wird
fetch('/api/accounts/sso/initiate/', {
    credentials: 'include',  // ← Wichtig!
    // ...
});
```

---

### ❌ **Problem 3: SSO Token schon verwendet**

```json
{
  "error": "SSO token has expired or already been used"
}
```

**Ursache:** SSO Token kann nur **einmal** verwendet werden (security feature).

**Lösung:**
- Neuen SSO-Flow starten
- Token nicht mehrfach verwenden
- Token ist 5 Minuten gültig

---

### ❌ **Problem 4: CORS Fehler**

**Ursache:** Website ist nicht in `allowed_origins` konfiguriert.

**Lösung:**
1. Im Auth-Service Admin Panel einloggen
2. Website bearbeiten
3. `allowed_origins` hinzufügen:
   ```
   https://palmservers.de
   https://auth.palmdynamicx.de
   https://website-b.com
   http://localhost:3000
   ```

---

### ❌ **Problem 5: Cross-Domain Cookies werden nicht gesendet**

**Ursache:** Browser blockiert Third-Party Cookies oder `SameSite` Policy verhindert Cookie-Übertragung.

**Symptom:**
```json
{
  "authenticated": false,
  "message": "User must login first"
}
```

**Obwohl User auf palmservers.de eingeloggt ist!**

**Lösung:** Verwende den **SSO Status Check** Flow:

```javascript
// Auf Website B (auth.palmdynamicx.de)
async function checkIfUserIsLoggedInAnywhere() {
    try {
        // Prüfe SSO-Status beim Auth-Service
        const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/status/', {
            method: 'POST',
            credentials: 'include', // Versucht Cookies zu senden
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'your-api-key'
            },
            body: JSON.stringify({
                website_id: 'your-website-id'
            })
        });
        
        const data = await response.json();
        
        if (data.sso_available) {
            console.log('✅ User ist irgendwo eingeloggt!');
            // Jetzt SSO initiieren
            return true;
        } else {
            console.log('❌ User muss sich anmelden');
            return false;
        }
    } catch (error) {
        console.error('SSO Check failed:', error);
        return false;
    }
}
```

**Wichtig für Cross-Domain:**
- Browser müssen `credentials: 'include'` unterstützen
- Auth-Service muss CORS korrekt konfiguriert haben
- `Access-Control-Allow-Credentials: true` muss gesetzt sein
- Moderne Browser (Chrome, Firefox, Safari) unterstützen dies

---

## 🔒 Sicherheitshinweise

### ✅ Best Practices

1. **API Keys schützen**
   - Nie im Frontend Code speichern
   - Nur im Backend verwenden
   - Regelmäßig rotieren

2. **HTTPS verwenden**
   - Alle SSO Requests über HTTPS
   - Session Cookies mit `Secure` Flag

3. **Token Expiry**
   - SSO Token: 5 Minuten
   - Nur einmal verwendbar
   - Nach Verwendung gelöscht

4. **IP Validation**
   - Optional: IP-Adresse prüfen
   - Verhindert Token-Diebstahl

5. **Session Management**
   - Session Cookies mit `HttpOnly`
   - `SameSite=Lax` oder `Strict`
   - Sichere Ablaufzeiten

---

## 🧪 Testing

### Test 1: SSO Status prüfen

```bash
# Prüfe ob User SSO-fähig ist
curl -X POST https://auth.palmdynamicx.de/api/accounts/sso/status/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "website_id": "8bc78e67-b249-4e86-b44a-ace71b9a868a"
  }'
```

### Test 2: SSO initiieren

```bash
# Mit Session Cookie
curl -X POST https://auth.palmdynamicx.de/api/accounts/sso/initiate/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Cookie: sessionid=YOUR_SESSION_COOKIE" \
  -d '{
    "website_id": "8bc78e67-b249-4e86-b44a-ace71b9a868a",
    "redirect_uri": "https://website-b.com/auth/callback"
  }'
```

### Test 3: Token austauschen

```bash
# SSO Token gegen JWT austauschen
curl -X POST https://auth.palmdynamicx.de/api/accounts/sso/callback/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "sso_token": "RECEIVED_SSO_TOKEN",
    "website_id": "8bc78e67-b249-4e86-b44a-ace71b9a868a"
  }'
```

---

## 📊 Vollständiger Flow: Ende-zu-Ende

### Szenario 1: Cross-Domain SSO (palmservers.de → auth.palmdynamicx.de)

```javascript
// =====================================================
// WEBSITE A: palmservers.de (User ist hier eingeloggt)
// =====================================================

// User klickt auf "Zu Auth-Service" Button
function goToAuthService() {
    const AUTH_SERVICE = 'https://auth.palmdynamicx.de';
    const WEBSITE_B_ID = '8bc78e67-b249-4e86-b44a-ace71b9a868a';
    const CALLBACK_URL = encodeURIComponent('https://auth.palmdynamicx.de/auth/sso-callback');
    
    // Redirect zum Auth-Service SSO Endpoint
    // Der Auth-Service wird prüfen ob User eine Session hat
    window.location.href = `${AUTH_SERVICE}/api/accounts/sso/initiate/?website_id=${WEBSITE_B_ID}&redirect_uri=${CALLBACK_URL}`;
}

// =====================================================
// AUTH-SERVICE: Prüft Session und generiert Token
// =====================================================
// (Dies passiert automatisch im Backend)
// Wenn User Session hat → SSO Token generieren
// Wenn User keine Session hat → Redirect zu Login

// =====================================================
// WEBSITE B: auth.palmdynamicx.de (Empfängt SSO Token)
// =====================================================

// Diese Seite wird aufgerufen: /auth/sso-callback?sso_token=xyz123

async function handleSSOCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const ssoToken = urlParams.get('sso_token');
    
    if (!ssoToken) {
        console.log('Kein SSO Token - User muss sich normal anmelden');
        window.location.href = '/login';
        return;
    }
    
    console.log('✅ SSO Token erhalten:', ssoToken);
    
    try {
        // Token gegen JWT austauschen
        const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/callback/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'website-b-api-key'
            },
            body: JSON.stringify({
                sso_token: ssoToken,
                website_id: '8bc78e67-b249-4e86-b44a-ace71b9a868a'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // JWT Tokens speichern
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            console.log('🎉 Cross-Domain SSO erfolgreich!');
            console.log('User:', data.user.email);
            console.log('Von palmservers.de zu auth.palmdynamicx.de eingeloggt!');
            
            // Redirect zur gewünschten Seite
            window.location.href = '/dashboard';
        } else {
            console.error('SSO Token Austausch fehlgeschlagen');
            window.location.href = '/login?error=sso_failed';
        }
    } catch (error) {
        console.error('SSO Error:', error);
        window.location.href = '/login?error=network_error';
    }
}

// Bei Seiten-Load ausführen
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleSSOCallback);
} else {
    handleSSOCallback();
}
```

---

### Szenario 2: Same-Domain SSO (shop.palmdynamicx.de → blog.palmdynamicx.de)

```javascript
// ===================================
// WEBSITE A (Shop) - Initiiert SSO
// ===================================

// 1. User klickt "Zum Blog" Button
async function goToBlog() {
    const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/initiate/', {
        method: 'POST',
        credentials: 'include', // Session Cookie!
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'shop-api-key'
        },
        body: JSON.stringify({
            website_id: 'blog-website-id',
            redirect_uri: 'https://blog.example.com/auth/sso'
        })
    });
    
    const data = await response.json();
    
    if (data.authenticated && data.redirect_url) {
        // User ist eingeloggt - Redirect mit SSO Token
        window.location.href = data.redirect_url;
    } else {
        // User nicht eingeloggt - zu Login
        window.location.href = data.login_url;
    }
}

// ===================================
// WEBSITE B (Blog) - Empfängt SSO
// ===================================

// 2. Blog empfängt Redirect mit SSO Token
// URL: https://blog.example.com/auth/sso?sso_token=abc123

async function processSSOLogin() {
    const urlParams = new URLSearchParams(window.location.search);
    const ssoToken = urlParams.get('sso_token');
    
    // 3. Token gegen JWT austauschen
    const response = await fetch('https://auth.palmdynamicx.de/api/accounts/sso/callback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'blog-api-key'
        },
        body: JSON.stringify({
            sso_token: ssoToken,
            website_id: 'blog-website-id'
        })
    });
    
    const data = await response.json();
    
    // 4. JWT Tokens speichern
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    // 5. User ist eingeloggt!
    console.log('Willkommen', data.user.email);
    window.location.href = '/dashboard';
}
```

---

## 🎓 Zusammenfassung

### Was du gelernt hast:

✅ **SSO ermöglicht** automatisches Login über mehrere Websites  
✅ **Cross-Domain SSO** funktioniert auch über verschiedene Domains (palmservers.de → auth.palmdynamicx.de)  
✅ **Flow:** Initiate → Token generieren → Token austauschen → JWT erhalten  
✅ **Sicherheit:** Session Cookies, API Keys, Token Expiry  
✅ **Implementation:** Frontend + Backend Code Examples  
✅ **Troubleshooting:** Häufige Fehler und Lösungen inkl. Cross-Domain  

### Wichtigste Punkte:

1. 🔑 **SSO basiert auf Sessions, nicht JWT**
2. 🍪 **Session Cookie muss mitgesendet werden**
3. 🌐 **Cross-Domain SSO:** palmservers.de → auth.palmdynamicx.de funktioniert!
4. ⏱️ **SSO Token gültig für 5 Minuten**
5. ☝️ **Token nur einmal verwendbar**
6. 🔒 **API Keys nur im Backend**
7. 🔄 **Redirect-basierter Flow** für beste Cross-Domain Kompatibilität

---

## 📞 Hilfe & Support

Bei Fragen oder Problemen:
- 📖 Siehe: [SSO_SYSTEM.md](SSO_SYSTEM.md) für detaillierte Dokumentation
- 🔧 Siehe: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) für mehr Beispiele
- 🐛 Siehe: [ERROR_HANDLING.md](ERROR_HANDLING.md) für Fehlerbehandlung

**Viel Erfolg mit SSO!** 🚀
