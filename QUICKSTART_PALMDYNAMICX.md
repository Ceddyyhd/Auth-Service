# 🎯 Schnellstart für auth.palmdynamicx.de

## 🚀 API-Dokumentation

Die interaktive API-Dokumentation ist verfügbar unter:

```
https://auth.palmdynamicx.de/api/docs/
```

**Features:**
- ✅ Swagger UI - Interaktive API-Tests
- ✅ Alle Endpoints dokumentiert
- ✅ Request/Response-Beispiele
- ✅ JWT-Token-Authentifizierung
- ✅ "Try it out"-Funktion

---

## 🔗 API von Ihrer Website aufrufen

### 1. JavaScript-Client herunterladen

```bash
# Laden Sie auth-client.js herunter
wget https://auth.palmdynamicx.de/static/auth-client.js
```

Oder verwenden Sie den Code aus [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md).

### 2. In HTML einbinden

```html
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <form id="login-form">
        <input type="email" id="email" placeholder="E-Mail" required>
        <input type="password" id="password" placeholder="Passwort" required>
        <button type="submit">Login</button>
    </form>
    
    <script>
        // Auth Client initialisieren
        const authClient = new AuthClient({
            apiUrl: 'https://auth.palmdynamicx.de',
            websiteId: 'IHRE-WEBSITE-UUID'  // Aus Admin-Panel
        });
        
        // Login-Handler
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const result = await authClient.login(email, password);
            
            if (result.success) {
                console.log('✅ Login erfolgreich:', result.user);
                window.location.href = '/dashboard';
            } else {
                alert('❌ Login fehlgeschlagen: ' + result.error);
            }
        });
    </script>
</body>
</html>
```

### 3. Geschützte API-Anfragen

```javascript
// Profil abrufen
const user = await authClient.getProfile();
console.log('User:', user);

// Profil aktualisieren
await authClient.updateProfile({
    first_name: 'Max',
    city: 'Berlin'
});

// Logout
await authClient.logout();
```

---

## 🔐 Sicherheit

### HTTPS ist PFLICHT

```javascript
// ✅ RICHTIG - Produktion
const authClient = new AuthClient({
    apiUrl: 'https://auth.palmdynamicx.de'
});

// ⚠️ NUR für lokale Entwicklung
const authClient = new AuthClient({
    apiUrl: 'http://localhost:8000'
});
```

### CORS-Konfiguration

Ihre Website muss im Auth-Service registriert sein:

1. **Admin-Panel öffnen:**
   ```
   https://auth.palmdynamicx.de/admin/
   ```

2. **Neue Website erstellen:**
   - Name: Ihre Website
   - Domain: ihre-website.de
   - Callback URL: https://ihre-website.de/auth/callback
   - Allowed Origins: ["https://ihre-website.de"]

3. **Website-ID kopieren** und im Client verwenden

---

## 📚 Vollständige Dokumentation

| Dokument | Beschreibung |
|----------|--------------|
| [API_REFERENCE.md](API_REFERENCE.md) | Detaillierte API-Referenz mit allen Endpoints |
| [SECURITY.md](SECURITY.md) | Sicherheits-Guide und Best Practices |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Vollständiger Integration-Guide mit Code-Beispielen |
| [DEPLOYMENT_PALMDYNAMICX.md](DEPLOYMENT_PALMDYNAMICX.md) | Server-Deployment und Konfiguration |

---

## 🎨 Frameworks

### React

```javascript
import { useAuth } from './auth/AuthProvider';

function LoginPage() {
    const { login } = useAuth();
    
    async function handleLogin(email, password) {
        const result = await login(email, password);
        if (result.success) {
            navigate('/dashboard');
        }
    }
}
```

[Vollständige React-Integration](INTEGRATION_GUIDE.md#react-integration)

### Vue.js

```javascript
// composables/useAuth.js
import { ref } from 'vue';

export function useAuth() {
    const user = ref(null);
    const authClient = new AuthClient({
        apiUrl: 'https://auth.palmdynamicx.de',
        websiteId: 'YOUR-UUID'
    });
    
    async function login(email, password) {
        const result = await authClient.login(email, password);
        if (result.success) {
            user.value = result.user;
        }
        return result;
    }
    
    return { user, login };
}
```

### Angular

```typescript
// auth.service.ts
import { Injectable } from '@angular/core';
import { AuthClient } from './auth-client';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authClient: AuthClient;
  
  constructor() {
    this.authClient = new AuthClient({
      apiUrl: 'https://auth.palmdynamicx.de',
      websiteId: environment.websiteId
    });
  }
  
  async login(email: string, password: string) {
    return await this.authClient.login(email, password);
  }
}
```

---

## 🔧 Verfügbare Endpoints

### Authentifizierung

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/accounts/register/` | POST | Neuen Benutzer registrieren |
| `/api/accounts/login/` | POST | Benutzer anmelden |
| `/api/accounts/logout/` | POST | Benutzer abmelden |
| `/api/token/refresh/` | POST | Access-Token erneuern |

### Benutzer-Verwaltung

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/accounts/profile/` | GET | Profil abrufen |
| `/api/accounts/profile/` | PATCH | Profil aktualisieren |
| `/api/accounts/change-password/` | POST | Passwort ändern |
| `/api/accounts/verify-email/` | POST | E-Mail verifizieren |

### Permissions & Rollen

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/permissions/` | GET | Alle Permissions |
| `/api/permissions/check/me/` | GET | Eigene Permissions |
| `/api/roles/` | GET | Alle Rollen |
| `/api/roles/{id}/assign/` | POST | Rolle zuweisen |

[Vollständige API-Referenz](https://auth.palmdynamicx.de/api/docs/)

---

## 🧪 Testen

### Browser-Konsole

```javascript
// Client initialisieren
const client = new AuthClient({
    apiUrl: 'https://auth.palmdynamicx.de',
    websiteId: 'YOUR-UUID'
});

// Login testen
const result = await client.login('test@example.com', 'password123');
console.log('Login:', result);

// Profil abrufen
const user = await client.getProfile();
console.log('User:', user);

// Logout
await client.logout();
```

### CURL

```bash
# Login
curl -X POST https://auth.palmdynamicx.de/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"password123"}'

# Profil abrufen (mit Token)
curl -X GET https://auth.palmdynamicx.de/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 💡 Beispiel-Anwendungen

### Vollständiges Login-Formular

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>PalmDynamicX Login</title>
    <style>
        .container { max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        input { width: 100%; padding: 10px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form id="login-form">
            <div class="form-group">
                <input type="email" id="email" placeholder="E-Mail" required>
            </div>
            <div class="form-group">
                <input type="password" id="password" placeholder="Passwort" required>
            </div>
            <button type="submit">Anmelden</button>
        </form>
        <div id="message"></div>
        
        <p>
            Noch kein Account? <a href="register.html">Registrieren</a><br>
            <a href="forgot-password.html">Passwort vergessen?</a>
        </p>
    </div>
    
    <script>
        const authClient = new AuthClient({
            apiUrl: 'https://auth.palmdynamicx.de',
            websiteId: 'YOUR-WEBSITE-UUID'
        });
        
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = 'Anmeldung läuft...';
            messageDiv.className = '';
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const result = await authClient.login(email, password);
            
            if (result.success) {
                messageDiv.textContent = '✅ Erfolgreich angemeldet! Weiterleitung...';
                messageDiv.className = 'success';
                
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                messageDiv.textContent = '❌ ' + result.error;
                messageDiv.className = 'error';
            }
        });
    </script>
</body>
</html>
```

---

## 📞 Support

- **API-Dokumentation:** https://auth.palmdynamicx.de/api/docs/
- **Admin-Panel:** https://auth.palmdynamicx.de/admin/
- **E-Mail:** support@palmdynamicx.de
- **GitHub:** https://github.com/PalmDynamicX/Auth-Service

---

## ✅ Checkliste für Integration

- [ ] Website im Admin-Panel registriert
- [ ] Website-ID kopiert
- [ ] Domain in CORS eingetragen
- [ ] auth-client.js eingebunden
- [ ] Login funktioniert
- [ ] Token-Refresh funktioniert
- [ ] Logout funktioniert
- [ ] HTTPS aktiviert (Produktion)

---

**Viel Erfolg! 🚀**
