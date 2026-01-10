# 🚨 Error Handling - Vollständiger Leitfaden

## Übersicht

Der Auth-Service nutzt ein fortschrittliches Error-Handling-System, das **detaillierte JSON-Fehlerantworten** statt HTML-Fehlerseiten zurückgibt. Jeder Fehler enthält:

✅ **Klare Fehlerbeschreibung**  
✅ **Mögliche Ursachen**  
✅ **Lösungsvorschläge**  
✅ **Nutzungshinweise mit Beispielen**  
✅ **Code-Beispiele (cURL, JavaScript)**

---

## 🎯 Fehlerstruktur

Alle API-Fehlerantworten folgen diesem Format:

```json
{
  "error": true,
  "error_type": "Exception",
  "message": "Fehlerbeschreibung",
  "endpoint": "/api/accounts/login/",
  "method": "POST",
  "usage_guide": {
    "description": "Endpunkt-Beschreibung",
    "required_headers": {},
    "required_fields": {},
    "optional_fields": {},
    "possible_errors": {}
  },
  "example": {
    "curl": "curl Beispiel...",
    "javascript": "fetch Beispiel..."
  }
}
```

---

## 📋 Fehlertypen und Beispiele

### 1️⃣ **500 Internal Server Error** - API-Key fehlt

**Fehler:**
```json
{
  "error": true,
  "message": "API-Key fehlt oder ist ungültig",
  "required_header": "X-API-Key",
  "how_to_get": "Registrieren Sie eine Website im Auth-Service Admin-Panel",
  "admin_url": "https://auth.palmdynamicx.de/admin/",
  "example": {
    "curl": "curl -H \"X-API-Key: YOUR_API_KEY\" ...",
    "javascript": "headers: { \"X-API-Key\": \"YOUR_API_KEY\" }"
  }
}
```

**Lösung:**
1. Gehe zu https://auth.palmdynamicx.de/admin/
2. Erstelle eine Website unter "Accounts → Websites"
3. Kopiere den generierten API-Key
4. Füge den Header hinzu: `X-API-Key: YOUR_API_KEY`

---

### 2️⃣ **400 Bad Request** - Fehlende Felder

**Fehler:**
```json
{
  "error": true,
  "message": "Username und Password sind erforderlich",
  "missing_fields": ["password"],
  "required_fields": {
    "username": "E-Mail-Adresse oder Benutzername",
    "password": "Passwort"
  },
  "optional_fields": {
    "mfa_token": "6-stelliger Code (nur wenn MFA aktiviert)"
  },
  "example": {
    "username": "user@example.com",
    "password": "YourPassword123!"
  }
}
```

**Lösung:**
Stelle sicher, dass alle erforderlichen Felder gesendet werden:

```javascript
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    username: 'user@example.com',  // ✅ Erforderlich
    password: 'SecurePass123!'      // ✅ Erforderlich
  })
});
```

---

### 3️⃣ **401 Unauthorized** - Ungültige Anmeldedaten

**Fehler:**
```json
{
  "error": true,
  "message": "Ungültige Anmeldedaten",
  "details": "Kein aktiver Account mit diesen Zugangsdaten gefunden",
  "possible_reasons": [
    "E-Mail oder Passwort ist falsch",
    "Account existiert nicht",
    "Account wurde deaktiviert",
    "E-Mail wurde noch nicht verifiziert (prüfen Sie Ihr Postfach)"
  ],
  "next_steps": [
    "Überprüfen Sie Ihre Eingaben",
    "Passwort vergessen? Nutzen Sie /api/accounts/password-reset/request/",
    "Noch kein Account? Registrieren Sie sich unter /api/accounts/register/"
  ]
}
```

**Lösungen:**
1. **Passwort zurücksetzen:**
   ```bash
   curl -X POST https://auth.palmdynamicx.de/api/accounts/password-reset/request/ \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{"email": "user@example.com"}'
   ```

2. **Neuen Account erstellen:**
   ```bash
   curl -X POST https://auth.palmdynamicx.de/api/accounts/register/ \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
       "email": "new@example.com",
       "username": "newuser",
       "password": "SecurePass123!",
       "password_confirm": "SecurePass123!"
     }'
   ```

---

### 4️⃣ **401 Unauthorized** - Ungültiger MFA-Code

**Fehler:**
```json
{
  "error": true,
  "message": "Ungültiger MFA-Code",
  "details": "Der eingegebene 6-stellige Code ist falsch oder abgelaufen",
  "mfa_type": "TOTP (Time-based One-Time Password)",
  "hints": [
    "Codes ändern sich alle 30 Sekunden",
    "Stellen Sie sicher, dass die Zeit auf Ihrem Gerät korrekt ist",
    "Nutzen Sie einen aktuellen Code aus Ihrer Authenticator-App"
  ],
  "backup_codes": "Falls Sie keinen Zugriff auf Ihr Gerät haben, nutzen Sie einen Backup-Code"
}
```

**Lösungen:**
1. Warte auf einen neuen Code (ändern sich alle 30 Sekunden)
2. Prüfe die Systemzeit auf deinem Gerät
3. Nutze einen Backup-Code als Alternative

---

### 5️⃣ **403 Forbidden** - Kein Website-Zugriff

**Fehler:**
```json
{
  "error": true,
  "message": "Zugriff verweigert",
  "details": "Sie haben keinen Zugriff auf die Website \"Blog Website\"",
  "website": {
    "name": "Blog Website",
    "id": "abc-123-def",
    "require_access": true
  },
  "reason": "Website erfordert explizite Zugriffsberechtigung",
  "solution": "Kontaktieren Sie den Website-Administrator für Zugriff"
}
```

**Lösung:**
Kontaktiere den Administrator der Website, um Zugriff zu erhalten.

---

## 🔍 Debugging mit detaillierten Fehlern

### DEBUG Mode (nur Development!)

Wenn `DEBUG = True` in settings.py, werden zusätzliche Informationen zurückgegeben:

```json
{
  "error": true,
  "message": "Database connection failed",
  "traceback": "Traceback (most recent call last):\n  File ...",
  "endpoint": "/api/accounts/login/",
  "method": "POST"
}
```

⚠️ **Wichtig:** Setze `DEBUG = False` in Production!

---

## 📖 Usage Guides für alle Endpunkte

Die Middleware gibt automatisch Nutzungshinweise für jeden Endpunkt zurück:

### Login (`/api/accounts/login/`)

```json
{
  "usage_guide": {
    "description": "Authentifiziert einen Benutzer und gibt JWT-Tokens zurück.",
    "required_headers": {
      "Content-Type": "application/json",
      "X-API-Key": "Ihr API-Schlüssel"
    },
    "required_fields": {
      "username": "E-Mail oder Benutzername",
      "password": "Passwort"
    },
    "optional_fields": {
      "mfa_token": "6-stelliger MFA-Code"
    },
    "possible_errors": {
      "400": "Username oder Password fehlt",
      "401": "Ungültige Anmeldedaten",
      "403": "Kein Zugriff auf diese Website",
      "500": "Interner Serverfehler"
    }
  },
  "example": {
    "curl": "curl -X POST ... (siehe oben)",
    "javascript": "const response = await fetch(...)"
  }
}
```

### Register (`/api/accounts/register/`)

```json
{
  "usage_guide": {
    "description": "Erstellt einen neuen Benutzer-Account.",
    "required_headers": {
      "Content-Type": "application/json",
      "X-API-Key": "Ihr API-Schlüssel"
    },
    "required_fields": {
      "email": "E-Mail-Adresse",
      "username": "Benutzername",
      "password": "Passwort",
      "password_confirm": "Passwortbestätigung"
    },
    "note": "Weitere Pflichtfelder abhängig von Website-Einstellungen"
  }
}
```

### Profile (`/api/accounts/profile/`)

```json
{
  "usage_guide": {
    "description": "Ruft Benutzerprofil ab oder aktualisiert es.",
    "required_headers": {
      "Authorization": "Bearer <access_token>"
    },
    "note": "Token aus Login-Response verwenden"
  }
}
```

### Permissions (`/api/permissions/...`)

```json
{
  "usage_guide": {
    "description": "Prüft Berechtigungen für einen Benutzer.",
    "required_headers": {
      "Authorization": "Bearer <access_token>",
      "X-API-Key": "Ihr API-Schlüssel"
    },
    "note": "Siehe PERMISSIONS_GUIDE.md für Details"
  }
}
```

---

## 🛠️ Implementierung

### Frontend - Error Handling

```javascript
async function handleAPIRequest(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    // Prüfe auf Fehler
    if (!response.ok || data.error) {
      console.error('API Error:', data);
      
      // Zeige Fehlermeldung dem Benutzer
      showError(data.message);
      
      // Zeige zusätzliche Details in Console
      if (data.usage_guide) {
        console.log('Usage Guide:', data.usage_guide);
      }
      if (data.example) {
        console.log('Example:', data.example);
      }
      if (data.next_steps) {
        console.log('Next Steps:', data.next_steps);
      }
      
      throw new Error(data.message);
    }
    
    return data;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}

// Verwendung
try {
  const data = await handleAPIRequest('https://auth.palmdynamicx.de/api/accounts/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify({
      username: 'user@example.com',
      password: 'SecurePass123!'
    })
  });
  
  console.log('Login successful:', data);
} catch (error) {
  // Fehler wurde bereits geloggt und angezeigt
}
```

### Backend - Error Handling (Python)

```python
import requests

def make_api_request(url, data, api_key):
    try:
        response = requests.post(
            url,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': api_key
            }
        )
        
        result = response.json()
        
        # Prüfe auf Fehler
        if result.get('error'):
            print(f"API Error: {result.get('message')}")
            
            # Zeige Usage Guide
            if 'usage_guide' in result:
                print(f"Usage Guide: {result['usage_guide']}")
            
            # Zeige Next Steps
            if 'next_steps' in result:
                print(f"Next Steps: {result['next_steps']}")
            
            raise Exception(result.get('message'))
        
        return result
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise

# Verwendung
try:
    data = make_api_request(
        'https://auth.palmdynamicx.de/api/accounts/login/',
        {
            'username': 'user@example.com',
            'password': 'SecurePass123!'
        },
        'YOUR_API_KEY'
    )
    print(f"Login successful: {data}")
except Exception as error:
    print(f"Login failed: {error}")
```

---

## 🔗 Status Codes

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **200** | OK | Erfolgreiche Anfrage |
| **201** | Created | Ressource erstellt (z.B. Registrierung) |
| **400** | Bad Request | Fehlende oder ungültige Parameter |
| **401** | Unauthorized | Authentifizierung fehlgeschlagen |
| **403** | Forbidden | Keine Berechtigung |
| **404** | Not Found | Endpunkt existiert nicht |
| **500** | Internal Server Error | Serverfehler (z.B. fehlender API-Key) |

---

## 💡 Best Practices

### ✅ DO:

1. **Prüfe immer `response.ok` und `data.error`**
   ```javascript
   if (!response.ok || data.error) {
     // Handle error
   }
   ```

2. **Logge Fehlerdetails für Debugging**
   ```javascript
   console.error('API Error:', {
     message: data.message,
     usage_guide: data.usage_guide,
     example: data.example
   });
   ```

3. **Zeige benutzerfreundliche Fehlermeldungen**
   ```javascript
   showError(data.message); // "Ungültige Anmeldedaten"
   // NICHT: showError("Error 401")
   ```

4. **Nutze die Beispiele aus der Error-Response**
   ```javascript
   if (data.example) {
     console.log('How to use:', data.example.curl);
   }
   ```

### ❌ DON'T:

1. **Ignoriere Fehlerdetails nicht**
   ```javascript
   // ❌ Schlecht
   catch (error) {
     console.log("Error");
   }
   
   // ✅ Gut
   catch (error) {
     console.error("API Error:", error.message, error.details);
   }
   ```

2. **Verlass dich nicht nur auf Status Codes**
   ```javascript
   // ❌ Schlecht
   if (response.status === 401) { ... }
   
   // ✅ Gut
   if (data.error && data.message.includes("Anmeldedaten")) { ... }
   ```

---

## 📚 Weitere Dokumentation

- **API-Endpunkte**: [API_ENDPOINTS_COMPLETE.md](./API_ENDPOINTS_COMPLETE.md)
- **Berechtigungen**: [PERMISSIONS_GUIDE.md](./PERMISSIONS_GUIDE.md)
- **Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

**Ende der Dokumentation** | Stand: Januar 2026 | Version 1.0
