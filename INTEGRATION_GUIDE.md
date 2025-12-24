# 🔗 Website-Integration mit auth.palmdynamicx.de

Anleitung zur Integration der Auth API in Ihre Websites für sichere Cross-Origin-Authentifizierung.

## 📋 Übersicht

Diese Anleitung zeigt Ihnen, wie Sie die zentrale Auth API (`https://auth.palmdynamicx.de`) in Ihre Websites integrieren, um sichere Authentifizierung über mehrere Domains hinweg zu ermöglichen.

---

## 🚀 Schnellstart

### 1. Website registrieren

Registrieren Sie Ihre Website im Auth Service Admin:

```
URL: https://auth.palmdynamicx.de/admin/
```

Erstellen Sie einen neuen Website-Eintrag:
- **Name:** Meine Website
- **Domain:** beispiel.de
- **Callback URL:** https://beispiel.de/auth/callback
- **Allowed Origins:** ["https://beispiel.de", "https://www.beispiel.de"]

### 2. JavaScript-Client einbinden

```html
<!DOCTYPE html>
<html>
<head>
    <title>Meine Website</title>
</head>
<body>
    <!-- Login-Formular -->
    <div id="login-form">
        <input type="email" id="email" placeholder="E-Mail">
        <input type="password" id="password" placeholder="Passwort">
        <button onclick="login()">Login</button>
    </div>
    
    <!-- User-Info (nach Login) -->
    <div id="user-info" style="display:none;">
        <h2>Willkommen, <span id="username"></span>!</h2>
        <button onclick="logout()">Logout</button>
    </div>
    
    <script src="auth-client.js"></script>
    <script>
        // Initialisierung
        const authClient = new AuthClient({
            apiUrl: 'https://auth.palmdynamicx.de',
            websiteId: 'IHRE-WEBSITE-UUID-HIER'
        });
        
        // Beim Laden prüfen ob User eingeloggt ist
        window.addEventListener('load', async () => {
            if (authClient.isAuthenticated()) {
                await loadUserProfile();
            }
        });
        
        // Login-Funktion
        async function login() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const result = await authClient.login(email, password);
            
            if (result.success) {
                await loadUserProfile();
            } else {
                alert('Login fehlgeschlagen: ' + result.error);
            }
        }
        
        // User-Profil laden
        async function loadUserProfile() {
            const user = await authClient.getProfile();
            document.getElementById('username').textContent = user.first_name;
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('user-info').style.display = 'block';
        }
        
        // Logout
        async function logout() {
            await authClient.logout();
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('user-info').style.display = 'none';
        }
    </script>
</body>
</html>
```

---

## 📦 JavaScript-Client (auth-client.js)

Vollständiger, produktionsreifer Client für Cross-Origin-Auth:

```javascript
/**
 * PalmDynamicX Auth Client
 * Sichere Authentifizierung über Cross-Origin API
 * Version: 1.0.0
 */
class AuthClient {
    constructor(config) {
        this.apiUrl = config.apiUrl || 'https://auth.palmdynamicx.de';
        this.websiteId = config.websiteId;
        this.accessTokenKey = 'pdx_access_token';
        this.refreshTokenKey = 'pdx_refresh_token';
        this.userKey = 'pdx_user';
    }
    
    /**
     * Login mit E-Mail und Passwort
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiUrl}/api/accounts/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                return {
                    success: false,
                    error: data.detail || 'Login fehlgeschlagen'
                };
            }
            
            // Tokens speichern
            this.setTokens(data.access, data.refresh);
            
            // User-Daten speichern
            if (data.user) {
                localStorage.setItem(this.userKey, JSON.stringify(data.user));
            }
            
            return {
                success: true,
                user: data.user,
                tokens: {
                    access: data.access,
                    refresh: data.refresh
                }
            };
            
        } catch (error) {
            console.error('Login-Fehler:', error);
            return {
                success: false,
                error: 'Netzwerkfehler: ' + error.message
            };
        }
    }
    
    /**
     * Registrierung
     */
    async register(userData) {
        try {
            const response = await fetch(`${this.apiUrl}/api/accounts/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    ...userData,
                    website_id: this.websiteId
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                return {
                    success: false,
                    error: data.error || 'Registrierung fehlgeschlagen',
                    details: data.details
                };
            }
            
            // Tokens speichern
            this.setTokens(data.tokens.access, data.tokens.refresh);
            
            // User-Daten speichern
            if (data.user) {
                localStorage.setItem(this.userKey, JSON.stringify(data.user));
            }
            
            return {
                success: true,
                user: data.user,
                message: data.message
            };
            
        } catch (error) {
            console.error('Registrierungs-Fehler:', error);
            return {
                success: false,
                error: 'Netzwerkfehler: ' + error.message
            };
        }
    }
    
    /**
     * Logout
     */
    async logout() {
        try {
            const refreshToken = this.getRefreshToken();
            
            await fetch(`${this.apiUrl}/api/accounts/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAccessToken()}`
                },
                credentials: 'include',
                body: JSON.stringify({
                    refresh: refreshToken
                })
            });
            
        } catch (error) {
            console.error('Logout-Fehler:', error);
        } finally {
            // Lokal immer aufräumen
            this.clearTokens();
        }
    }
    
    /**
     * Profil abrufen
     */
    async getProfile() {
        const response = await this.authenticatedFetch('/api/accounts/profile/');
        const user = await response.json();
        localStorage.setItem(this.userKey, JSON.stringify(user));
        return user;
    }
    
    /**
     * Profil aktualisieren
     */
    async updateProfile(updates) {
        const response = await this.authenticatedFetch('/api/accounts/profile/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });
        
        const user = await response.json();
        localStorage.setItem(this.userKey, JSON.stringify(user));
        return user;
    }
    
    /**
     * Authentifizierte API-Anfrage
     */
    async authenticatedFetch(endpoint, options = {}) {
        const token = this.getAccessToken();
        
        if (!token) {
            throw new Error('Nicht authentifiziert');
        }
        
        const response = await fetch(`${this.apiUrl}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        // Token-Refresh bei 401
        if (response.status === 401) {
            const refreshed = await this.refreshToken();
            
            if (refreshed) {
                // Retry mit neuem Token
                return this.authenticatedFetch(endpoint, options);
            } else {
                // Logout bei fehlgeschlagenem Refresh
                this.clearTokens();
                window.location.href = '/login';
                throw new Error('Session abgelaufen');
            }
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error || 'API-Fehler');
        }
        
        return response;
    }
    
    /**
     * Access Token erneuern
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        
        if (!refreshToken) {
            return false;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/api/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    refresh: refreshToken
                })
            });
            
            if (!response.ok) {
                return false;
            }
            
            const data = await response.json();
            this.setTokens(data.access, refreshToken);
            
            return true;
            
        } catch (error) {
            console.error('Token-Refresh-Fehler:', error);
            return false;
        }
    }
    
    /**
     * Prüft ob User eingeloggt ist
     */
    isAuthenticated() {
        const token = this.getAccessToken();
        
        if (!token) {
            return false;
        }
        
        try {
            // Token decodieren (nur Payload)
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expirationTime = payload.exp * 1000;
            
            // Prüfen ob abgelaufen
            return Date.now() < expirationTime;
        } catch {
            return false;
        }
    }
    
    /**
     * Gibt gespeicherten User zurück
     */
    getCurrentUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    }
    
    /**
     * Token-Management
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem(this.accessTokenKey, accessToken);
        localStorage.setItem(this.refreshTokenKey, refreshToken);
    }
    
    getAccessToken() {
        return localStorage.getItem(this.accessTokenKey);
    }
    
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }
    
    clearTokens() {
        localStorage.removeItem(this.accessTokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
    }
}

// Für CommonJS/Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthClient;
}
```

---

## 🔐 Sicherheits-Best-Practices

### 1. HTTPS verwenden

```javascript
// ✅ RICHTIG - HTTPS
const authClient = new AuthClient({
    apiUrl: 'https://auth.palmdynamicx.de'
});

// ❌ FALSCH - HTTP (nur für lokale Entwicklung!)
const authClient = new AuthClient({
    apiUrl: 'http://localhost:8000'
});
```

### 2. Website-ID sicher handhaben

```javascript
// ✅ RICHTIG - Aus Umgebungsvariable
const authClient = new AuthClient({
    apiUrl: 'https://auth.palmdynamicx.de',
    websiteId: process.env.WEBSITE_ID  // In Build-Zeit injiziert
});

// ❌ FALSCH - Hardcoded im Source-Code
const authClient = new AuthClient({
    websiteId: 'f47ac10b-58cc-4372-a567-0e02b2c3d479'  // Nicht im öffentlichen Code!
});
```

### 3. Tokens niemals im URL übergeben

```javascript
// ❌ FALSCH - Token in URL
window.location.href = '/dashboard?token=' + accessToken;

// ✅ RICHTIG - Token in localStorage
localStorage.setItem('access_token', accessToken);
window.location.href = '/dashboard';
```

### 4. CORS-Header validieren

Der Auth-Service akzeptiert nur Anfragen von registrierten Domains. Stellen Sie sicher, dass Ihre Domain in `CORS_ALLOWED_ORIGINS` eingetragen ist.

---

## 🎨 React-Integration

### Custom Hook für Auth:

```javascript
import { useState, useEffect, createContext, useContext } from 'react';

// Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const authClient = new AuthClient({
        apiUrl: 'https://auth.palmdynamicx.de',
        websiteId: process.env.REACT_APP_WEBSITE_ID
    });
    
    useEffect(() => {
        // Beim Laden prüfen ob eingeloggt
        if (authClient.isAuthenticated()) {
            loadUser();
        } else {
            setLoading(false);
        }
    }, []);
    
    async function loadUser() {
        try {
            const userData = await authClient.getProfile();
            setUser(userData);
        } catch (error) {
            console.error('User laden fehlgeschlagen:', error);
        } finally {
            setLoading(false);
        }
    }
    
    async function login(email, password) {
        const result = await authClient.login(email, password);
        if (result.success) {
            setUser(result.user);
        }
        return result;
    }
    
    async function register(userData) {
        const result = await authClient.register(userData);
        if (result.success) {
            setUser(result.user);
        }
        return result;
    }
    
    async function logout() {
        await authClient.logout();
        setUser(null);
    }
    
    const value = {
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        authClient
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom Hook
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth muss innerhalb von AuthProvider verwendet werden');
    }
    return context;
}
```

### Verwendung in Komponenten:

```javascript
// App.js
import { AuthProvider } from './auth/AuthProvider';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

// LoginPage.js
import { useAuth } from './auth/AuthProvider';

function LoginPage() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    
    async function handleSubmit(e) {
        e.preventDefault();
        const result = await login(email, password);
        
        if (result.success) {
            navigate('/dashboard');
        } else {
            alert(result.error);
        }
    }
    
    return (
        <form onSubmit={handleSubmit}>
            <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="E-Mail"
            />
            <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="Passwort"
            />
            <button type="submit">Login</button>
        </form>
    );
}

// Dashboard.js
import { useAuth } from './auth/AuthProvider';

function Dashboard() {
    const { user, logout } = useAuth();
    
    return (
        <div>
            <h1>Willkommen, {user.first_name}!</h1>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

// ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from './auth/AuthProvider';

function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
        return <div>Laden...</div>;
    }
    
    return isAuthenticated ? children : <Navigate to="/login" />;
}
```

---

## 🧪 Testing

### Test in Browser-Konsole:

```javascript
// Client initialisieren
const client = new AuthClient({
    apiUrl: 'https://auth.palmdynamicx.de',
    websiteId: 'IHRE-UUID'
});

// Login testen
await client.login('test@example.com', 'password123');

// Profil abrufen
const user = await client.getProfile();
console.log(user);

// Logout
await client.logout();
```

---

## 📚 API-Endpunkte

Alle verfügbaren Endpunkte finden Sie in der interaktiven Dokumentation:

```
https://auth.palmdynamicx.de/api/docs/
```

---

## ✅ Checkliste für Go-Live

- [ ] Website im Auth-Admin registriert
- [ ] Domain in `CORS_ALLOWED_ORIGINS` eingetragen
- [ ] Website-ID in Client konfiguriert
- [ ] HTTPS aktiviert
- [ ] Login funktioniert
- [ ] Registrierung funktioniert
- [ ] Token-Refresh funktioniert
- [ ] Logout funktioniert
- [ ] Error-Handling implementiert

---

## 📞 Support

Bei Problemen:
- API-Dokumentation: https://auth.palmdynamicx.de/api/docs/
- E-Mail: support@palmdynamicx.de

---

**Integration erfolgreich! 🎉**
