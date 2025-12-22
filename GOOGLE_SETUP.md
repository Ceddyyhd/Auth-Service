# 🔐 Google OAuth einrichten

## Schritt 1: Google Cloud Console

### 1.1 Projekt erstellen
1. Gehe zu: https://console.cloud.google.com/
2. Klicke auf **"Projekt erstellen"**
3. Name: z.B. "Auth Service" oder "Meine Website"
4. Klicke **"Erstellen"**

### 1.2 OAuth Consent Screen konfigurieren
1. Im Menü: **APIs & Dienste** → **OAuth-Zustimmungsbildschirm**
2. Wähle **"Extern"** (für öffentliche Apps)
3. Klicke **"Erstellen"**
4. Fülle aus:
   - **App-Name**: "Meine Website"
   - **Nutzer-Support-E-Mail**: deine@email.de
   - **Developer-Kontakt-E-Mail**: deine@email.de
5. Klicke **"Speichern und fortfahren"**
6. **Scopes**: Klicke "Scopes hinzufügen"
   - Wähle: `userinfo.email` ✅
   - Wähle: `userinfo.profile` ✅
7. Klicke **"Speichern und fortfahren"**
8. **Testnutzer** (optional für Entwicklung):
   - Füge deine Test-E-Mail hinzu
9. Klicke **"Speichern und fortfahren"**

### 1.3 OAuth2 Credentials erstellen
1. Im Menü: **APIs & Dienste** → **Anmeldedaten**
2. Klicke **"+ Anmeldedaten erstellen"**
3. Wähle **"OAuth-Client-ID"**
4. **Anwendungstyp**: "Webanwendung"
5. **Name**: "Auth Service Web Client"
6. **Autorisierte JavaScript-Ursprünge**:
   ```
   http://localhost:3000
   http://localhost:8000
   http://127.0.0.1:8000
   https://deine-domain.de
   ```
7. **Autorisierte Weiterleitungs-URIs**:
   ```
   http://localhost:8000/api/accounts/social-login/callback/
   http://127.0.0.1:8000/api/accounts/social-login/callback/
   https://deine-domain.de/api/accounts/social-login/callback/
   ```
8. Klicke **"Erstellen"**

### 1.4 Credentials kopieren
Nach dem Erstellen erscheint ein Pop-up mit:
- **Client-ID**: z.B. `123456789-abc.apps.googleusercontent.com`
- **Clientschlüssel**: z.B. `GOCSPX-xyz123abc`

**⚠️ WICHTIG: Speichere diese Werte!**

---

## Schritt 2: In dein Projekt eintragen

### 2.1 `.env` Datei bearbeiten

Öffne die Datei `.env` und trage ein:

```env
# Social Login Settings
# Google OAuth2
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xyz123abc
```

### 2.2 Django Site ID erstellen

Da `allauth` benötigt SITE_ID, musst du die Django Sites Tabelle erstellen:

```bash
# Aktiviere Virtual Environment
.\venv\Scripts\Activate.ps1

# Migriere Sites
python manage.py migrate sites

# Erstelle Site (nur einmal ausführen!)
python manage.py shell
```

Im Shell:
```python
from django.contrib.sites.models import Site

# Erstelle oder update die Site
site = Site.objects.get_or_create(id=1, defaults={
    'domain': 'localhost:8000',
    'name': 'Auth Service Local'
})[0]
print(f"Site erstellt: {site.domain}")
exit()
```

---

## Schritt 3: Server neu starten

```bash
python manage.py runserver
```

---

## Schritt 4: Testen

### Frontend Test (HTML/JavaScript):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Google Login Test</title>
    <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
    <h1>Google Login Test</h1>
    
    <!-- Google Sign-In Button -->
    <div id="g_id_onload"
         data-client_id="DEINE_CLIENT_ID_HIER"
         data-callback="handleCredentialResponse">
    </div>
    <div class="g_id_signin" data-type="standard"></div>

    <script>
        async function handleCredentialResponse(response) {
            // Google JWT Token
            const googleToken = response.credential;
            
            // Decode Token (nur zum Anzeigen)
            const payload = JSON.parse(atob(googleToken.split('.')[1]));
            console.log('Google Payload:', payload);
            
            // An Auth Service senden
            try {
                const result = await fetch('http://127.0.0.1:8000/api/accounts/social-login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        provider: 'google',
                        provider_user_id: payload.sub,
                        email: payload.email,
                        first_name: payload.given_name || '',
                        last_name: payload.family_name || '',
                        avatar_url: payload.picture || ''
                    })
                });
                
                const data = await result.json();
                console.log('Auth Service Response:', data);
                
                if (data.tokens) {
                    // Login erfolgreich!
                    localStorage.setItem('access_token', data.tokens.access);
                    alert('Erfolgreich eingeloggt! ✅');
                    
                    // Prüfe Profil-Vollständigkeit
                    if (!data.profile_completed) {
                        alert('Bitte vervollständige dein Profil');
                        // Zeige Formular
                    }
                }
            } catch (error) {
                console.error('Fehler:', error);
                alert('Login fehlgeschlagen ❌');
            }
        }
    </script>
</body>
</html>
```

### Mit React/TypeScript:

```typescript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

function LoginPage() {
    const handleGoogleSuccess = async (credentialResponse: any) => {
        // Decode Google JWT
        const decoded: any = jwtDecode(credentialResponse.credential);
        
        // An Auth Service senden
        const response = await fetch('http://127.0.0.1:8000/api/accounts/social-login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: 'google',
                provider_user_id: decoded.sub,
                email: decoded.email,
                first_name: decoded.given_name || '',
                last_name: decoded.family_name || '',
                avatar_url: decoded.picture || ''
            })
        });
        
        const data = await response.json();
        
        if (data.tokens) {
            localStorage.setItem('access_token', data.tokens.access);
            console.log('Login erfolgreich!', data);
        }
    };

    return (
        <GoogleOAuthProvider clientId="DEINE_CLIENT_ID">
            <div>
                <h1>Login mit Google</h1>
                <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => console.log('Login fehlgeschlagen')}
                />
            </div>
        </GoogleOAuthProvider>
    );
}
```

---

## 📋 Checkliste

- [ ] Google Cloud Projekt erstellt
- [ ] OAuth Consent Screen konfiguriert
- [ ] OAuth2 Client-ID erstellt
- [ ] Weiterleitungs-URIs hinzugefügt
- [ ] Client-ID und Secret in `.env` eingetragen
- [ ] Django Sites Migration ausgeführt
- [ ] Site mit ID=1 erstellt
- [ ] Server neu gestartet
- [ ] Frontend Test implementiert
- [ ] Login erfolgreich getestet ✅

---

## ❓ Häufige Probleme

### "redirect_uri_mismatch"
➜ Prüfe ob die Redirect URI in Google Console EXAKT mit deiner URL übereinstimmt
➜ Achte auf `http` vs `https` und trailing slashes

### "invalid_client"
➜ Client-ID oder Secret ist falsch
➜ Prüfe `.env` Datei
➜ Server neu starten nach Änderungen

### "Access blocked: This app's request is invalid"
➜ OAuth Consent Screen noch nicht verifiziert
➜ Füge dich als Testnutzer hinzu während der Entwicklung

### Site matching query does not exist
➜ Django Site wurde nicht erstellt
➜ Führe `python manage.py migrate sites` aus
➜ Erstelle Site mit ID=1 im Shell

---

## 🚀 Produktions-Deployment

### Für Production:

1. **Google Console**:
   - Füge Production-Domains zu authorized origins hinzu
   - Füge Production-Redirect-URIs hinzu
   - Verifiziere OAuth Consent Screen (Publishing Status: "In Production")

2. **Django**:
   - Setze `DEBUG=False` in `.env`
   - Verwende HTTPS (SSL-Zertifikat)
   - Ändere `ALLOWED_HOSTS` zu deiner Domain

3. **Sicherheit**:
   - Verwende Umgebungsvariablen für Secrets (niemals im Code!)
   - Aktiviere CSRF Protection
   - Verwende sichere Cookies

---

**Viel Erfolg! 🎉**
