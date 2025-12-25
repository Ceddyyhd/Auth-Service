# 🔧 Email-Verifizierungs-URL Problem - Lösung

## 🔴 Problem:

```
URL in E-Mail: https://auth.palmdynamicx.de/verify-email?token=xxx
Fehler: 404 Not Found
```

**Ursache:** Die API-Route ist unter `/api/accounts/verify-email/` aber die E-Mail zeigt auf `/verify-email`.

---

## ✅ Lösung 1: .env auf Backend-API-URL ändern (EMPFOHLEN)

### Für Server (Production):

```bash
cd /var/www/auth-service
nano .env
```

**Ändere diese Zeilen:**

```bash
# FALSCH (zeigt auf nicht existierende Route):
EMAIL_VERIFY_URL=https://auth.palmdynamicx.de/verify-email
PASSWORD_RESET_URL=https://auth.palmdynamicx.de/reset-password

# RICHTIG (zeigt auf Backend-API):
EMAIL_VERIFY_URL=https://auth.palmdynamicx.de/api/accounts/verify-email
PASSWORD_RESET_URL=https://auth.palmdynamicx.de/api/accounts/reset-password
```

**Service neu starten:**
```bash
sudo systemctl restart authservice
```

### Für Lokal (.env):

```bash
EMAIL_VERIFY_URL=http://localhost:8000/api/accounts/verify-email
PASSWORD_RESET_URL=http://localhost:8000/api/accounts/reset-password
```

---

## ✅ Lösung 2: Frontend-Integration (wenn du ein Frontend hast)

Falls du ein Frontend hast (React, Vue, Next.js, etc.):

### .env Konfiguration:

```bash
# Frontend-URLs (Frontend verarbeitet Token und ruft dann Backend auf)
EMAIL_VERIFY_URL=https://deine-frontend-domain.com/verify-email
PASSWORD_RESET_URL=https://deine-frontend-domain.com/reset-password
```

### Frontend muss dann:

**1. E-Mail-Verifizierung (z.B. React):**

```javascript
// In deiner Frontend Route: /verify-email
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState('loading');
    const token = searchParams.get('token');
    
    useEffect(() => {
        if (token) {
            // Backend API aufrufen
            fetch('https://auth.palmdynamicx.de/api/accounts/verify-email/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token })
            })
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    setStatus('success');
                } else {
                    setStatus('error');
                }
            })
            .catch(() => setStatus('error'));
        }
    }, [token]);
    
    return (
        <div>
            {status === 'loading' && <p>E-Mail wird verifiziert...</p>}
            {status === 'success' && <p>✅ E-Mail erfolgreich bestätigt!</p>}
            {status === 'error' && <p>❌ Fehler bei der Verifizierung</p>}
        </div>
    );
}
```

**2. Passwort-Reset (z.B. React):**

```javascript
// In deiner Frontend Route: /reset-password
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function ResetPassword() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [status, setStatus] = useState('idle');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            alert('Passwörter stimmen nicht überein');
            return;
        }
        
        try {
            const response = await fetch(
                'https://auth.palmdynamicx.de/api/accounts/reset-password/',
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, new_password: password })
                }
            );
            
            const data = await response.json();
            
            if (data.message) {
                setStatus('success');
                // Redirect to login after 2 seconds
                setTimeout(() => window.location.href = '/login', 2000);
            } else {
                setStatus('error');
            }
        } catch (error) {
            setStatus('error');
        }
    };
    
    return (
        <div>
            <h2>Neues Passwort festlegen</h2>
            {status === 'success' ? (
                <p>✅ Passwort erfolgreich geändert! Weiterleitung zum Login...</p>
            ) : (
                <form onSubmit={handleSubmit}>
                    <input
                        type="password"
                        placeholder="Neues Passwort"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Passwort bestätigen"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Passwort zurücksetzen</button>
                </form>
            )}
            {status === 'error' && <p>❌ Fehler beim Zurücksetzen</p>}
        </div>
    );
}
```

---

## ✅ Lösung 3: Standalone HTML-Seiten (ohne Framework)

Falls du kein Frontend-Framework hast, kannst du einfache HTML-Seiten erstellen:

### 1. Erstelle Frontend-Verzeichnis:

```bash
# Auf dem Server
mkdir -p /var/www/frontend
cd /var/www/frontend
```

### 2. Erstelle `verify-email.html`:

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Mail Verifizierung</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .success { color: #28a745; font-size: 24px; }
        .error { color: #dc3545; font-size: 24px; }
        .message { margin-top: 20px; font-size: 18px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>E-Mail Verifizierung</h1>
        
        <div id="loading">
            <div class="spinner"></div>
            <p>E-Mail wird verifiziert...</p>
        </div>
        
        <div id="success" class="hidden">
            <div class="success">✅</div>
            <div class="message">E-Mail erfolgreich bestätigt!</div>
            <p>Du kannst dich jetzt anmelden.</p>
        </div>
        
        <div id="error" class="hidden">
            <div class="error">❌</div>
            <div class="message">Fehler bei der Verifizierung</div>
            <p id="error-message"></p>
        </div>
    </div>
    
    <script>
        // Token aus URL holen
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (!token) {
            showError('Kein Token gefunden');
        } else {
            // Backend API aufrufen
            fetch('https://auth.palmdynamicx.de/api/accounts/verify-email/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message || data.success) {
                    showSuccess();
                } else {
                    showError(data.error || 'Unbekannter Fehler');
                }
            })
            .catch(error => {
                showError('Netzwerkfehler');
            });
        }
        
        function showSuccess() {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('success').classList.remove('hidden');
        }
        
        function showError(message) {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('error').classList.remove('hidden');
            document.getElementById('error-message').textContent = message;
        }
    </script>
</body>
</html>
```

### 3. Erstelle `reset-password.html`:

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Passwort zurücksetzen</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 100%;
        }
        h1 { text-align: center; color: #333; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #f5576c;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #f5576c;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: #d44554; }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .message {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Passwort zurücksetzen</h1>
        
        <form id="resetForm">
            <div class="form-group">
                <label for="password">Neues Passwort:</label>
                <input 
                    type="password" 
                    id="password" 
                    required 
                    minlength="8"
                    placeholder="Mindestens 8 Zeichen"
                >
            </div>
            
            <div class="form-group">
                <label for="confirmPassword">Passwort bestätigen:</label>
                <input 
                    type="password" 
                    id="confirmPassword" 
                    required
                    placeholder="Passwort wiederholen"
                >
            </div>
            
            <button type="submit" id="submitBtn">Passwort zurücksetzen</button>
        </form>
        
        <div id="successMessage" class="message success hidden">
            ✅ Passwort erfolgreich geändert! Weiterleitung...
        </div>
        
        <div id="errorMessage" class="message error hidden"></div>
    </div>
    
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        const form = document.getElementById('resetForm');
        
        if (!token) {
            showError('Kein Token gefunden');
            form.style.display = 'none';
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const submitBtn = document.getElementById('submitBtn');
            
            if (password !== confirmPassword) {
                showError('Passwörter stimmen nicht überein');
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Wird verarbeitet...';
            
            try {
                const response = await fetch(
                    'https://auth.palmdynamicx.de/api/accounts/reset-password/',
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            token: token, 
                            new_password: password 
                        })
                    }
                );
                
                const data = await response.json();
                
                if (data.message || response.ok) {
                    showSuccess();
                    form.style.display = 'none';
                    // Redirect nach 2 Sekunden
                    setTimeout(() => {
                        window.location.href = 'https://auth.palmdynamicx.de/';
                    }, 2000);
                } else {
                    showError(data.error || 'Fehler beim Zurücksetzen');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Passwort zurücksetzen';
                }
            } catch (error) {
                showError('Netzwerkfehler');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Passwort zurücksetzen';
            }
        });
        
        function showSuccess() {
            document.getElementById('successMessage').classList.remove('hidden');
            document.getElementById('errorMessage').classList.add('hidden');
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = '❌ ' + message;
            errorDiv.classList.remove('hidden');
            document.getElementById('successMessage').classList.add('hidden');
        }
    </script>
</body>
</html>
```

### 4. Nginx konfigurieren:

```bash
sudo nano /etc/nginx/sites-available/frontend
```

```nginx
server {
    listen 80;
    server_name auth.palmdynamicx.de;
    
    root /var/www/frontend;
    index index.html;
    
    # Frontend-Seiten
    location /verify-email {
        try_files /verify-email.html =404;
    }
    
    location /reset-password {
        try_files /reset-password.html =404;
    }
    
    # API-Requests an Backend weiterleiten
    location /api/ {
        proxy_pass http://unix:/run/authservice.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location / {
        try_files $uri $uri/ =404;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. .env anpassen:

```bash
EMAIL_VERIFY_URL=https://auth.palmdynamicx.de/verify-email
PASSWORD_RESET_URL=https://auth.palmdynamicx.de/reset-password
```

---

## 🎯 SCHNELLSTE LÖSUNG (jetzt sofort):

```bash
# Auf dem Server:
cd /var/www/auth-service
nano .env

# Ändere diese Zeilen zu:
EMAIL_VERIFY_URL=https://auth.palmdynamicx.de/api/accounts/verify-email
PASSWORD_RESET_URL=https://auth.palmdynamicx.de/api/accounts/reset-password

# Service neu starten:
sudo systemctl restart authservice
```

**Dann teste mit dem Token aus deiner E-Mail:**
```bash
curl -X POST https://auth.palmdynamicx.de/api/accounts/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token":"QZTTUV3WxrywRkbrzurFAcTlHzToNf26F-N-6Sx_kPE"}'
```

---

## 📚 Zusammenfassung:

| Lösung | Komplexität | Use Case |
|--------|-------------|----------|
| **Option 1: Backend-URL** | ⭐ Einfach | Keine Frontend-UI nötig, API-only |
| **Option 2: Frontend-Framework** | ⭐⭐⭐ Komplex | Wenn React/Vue/Next.js vorhanden |
| **Option 3: Standalone HTML** | ⭐⭐ Mittel | Schöne UI ohne Framework |

**Empfehlung:** Starte mit **Option 1** (Backend-URL) für sofortige Funktionalität, dann später **Option 3** (HTML-Seiten) für bessere UX.
