# Multi-Factor Authentication (MFA) System

## Übersicht

Das MFA-System bietet TOTP-basierte Zwei-Faktor-Authentifizierung für erhöhte Sicherheit. Benutzer können MFA aktivieren und Authenticator-Apps wie Google Authenticator, Microsoft Authenticator oder Authy verwenden.

## Features

- ✅ **TOTP (Time-based One-Time Password)** - Standard 6-stellige Codes
- ✅ **QR-Code Generierung** - Einfaches Setup mit Authenticator-Apps
- ✅ **Backup-Codes** - 10 Einmal-Codes für Notfälle
- ✅ **Manuelle Eingabe** - Alternative zum QR-Code
- ✅ **Integration in Login-Flow** - Automatische MFA-Abfrage beim Login
- ✅ **Admin-Interface** - Verwaltung von MFA-Geräten

---

## API Endpoints

### 1. MFA Status abrufen

**Endpoint:** `GET /api/accounts/mfa/status/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Request:**
```bash
curl -X GET http://localhost:8000/api/accounts/mfa/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Response:**
```json
{
  "mfa_enabled": true,
  "activated_at": "2025-12-22T10:30:00Z",
  "last_used": "2025-12-22T18:45:00Z",
  "backup_codes_count": 8
}
```

---

### 2. MFA aktivieren

**Endpoint:** `POST /api/accounts/mfa/enable/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Beschreibung:** Startet den MFA-Setup-Prozess. Generiert einen Secret-Key und gibt einen QR-Code sowie Backup-Codes zurück.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/mfa/enable/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "message": "MFA setup initiated. Please scan the QR code with your authenticator app and verify.",
  "secret_key": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "backup_codes": [
    "A1B2C3D4",
    "E5F6G7H8",
    "I9J0K1L2",
    "M3N4O5P6",
    "Q7R8S9T0",
    "U1V2W3X4",
    "Y5Z6A7B8",
    "C9D0E1F2",
    "G3H4I5J6",
    "K7L8M9N0"
  ],
  "manual_entry_key": "JBSWY3DPEHPK3PXP"
}
```

**Wichtig:**
- MFA ist nach diesem Schritt noch NICHT aktiv
- Backup-Codes sicher speichern (nur einmal angezeigt!)
- QR-Code mit Authenticator-App scannen
- Dann Endpoint `/mfa/verify-setup/` aufrufen

---

### 3. MFA Setup verifizieren

**Endpoint:** `POST /api/accounts/mfa/verify-setup/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Beschreibung:** Aktiviert MFA durch Bestätigung eines TOTP-Tokens. Erst nach erfolgreicher Verifizierung ist MFA aktiv.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/mfa/verify-setup/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

**Response (Erfolg):**
```json
{
  "message": "MFA has been successfully enabled",
  "backup_codes_count": 10
}
```

**Response (Fehler):**
```json
{
  "error": "Invalid token. Please try again."
}
```

---

### 4. MFA Token verifizieren

**Endpoint:** `POST /api/accounts/mfa/verify/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Beschreibung:** Verifiziert einen MFA-Token ohne Zustandsänderung. Nützlich zum Testen oder für Re-Authentifizierung.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/mfa/verify/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

**Response:**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

---

### 5. Backup-Codes neu generieren

**Endpoint:** `POST /api/accounts/mfa/backup-codes/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Beschreibung:** Generiert neue Backup-Codes. Alte Codes werden ungültig.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/mfa/backup-codes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

**Response:**
```json
{
  "message": "Backup codes have been regenerated",
  "backup_codes": [
    "X1Y2Z3A4",
    "B5C6D7E8",
    "F9G0H1I2",
    "J3K4L5M6",
    "N7O8P9Q0",
    "R1S2T3U4",
    "V5W6X7Y8",
    "Z9A0B1C2",
    "D3E4F5G6",
    "H7I8J9K0"
  ]
}
```

---

### 6. MFA deaktivieren

**Endpoint:** `POST /api/accounts/mfa/disable/`

**Berechtigung:** Authentifiziert (Bearer Token)

**Beschreibung:** Deaktiviert MFA für den Benutzer. Erfordert Passwort UND MFA-Token für maximale Sicherheit.

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/mfa/disable/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "YourCurrentPassword123!",
    "token": "123456"
  }'
```

**Response:**
```json
{
  "message": "MFA has been successfully disabled"
}
```

**Sicherheitshinweis:** Beide Faktoren (Passwort + MFA-Token) sind erforderlich, um MFA zu deaktivieren.

---

## Login mit MFA

### Standard-Login (ohne MFA)

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "access": "eyJ0eXAiOiJKV1QiLC..."
}
```

---

### Login mit MFA aktiviert (2-Schritt-Prozess)

#### Schritt 1: Initiales Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response (MFA erforderlich):**
```json
{
  "mfa_required": true,
  "temp_token": "temporary_session_token_xyz",
  "message": "MFA verification required"
}
```

#### Schritt 2: MFA-Token eingeben

**Request:**
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePassword123!",
    "mfa_token": "123456"
  }'
```

**Response (Erfolg):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLC...",
  "access": "eyJ0eXAiOiJKV1QiLC..."
}
```

---

## Frontend Integration

### React Beispiel - MFA Setup

```jsx
import React, { useState } from 'react';

function MFASetup() {
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationToken, setVerificationToken] = useState('');
  const [setupComplete, setSetupComplete] = useState(false);

  // Schritt 1: MFA aktivieren
  const enableMFA = async () => {
    const response = await fetch('http://localhost:8000/api/accounts/mfa/enable/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    const data = await response.json();
    setQrCode(data.qr_code);
    setBackupCodes(data.backup_codes);
  };

  // Schritt 2: Setup verifizieren
  const verifySetup = async () => {
    const response = await fetch('http://localhost:8000/api/accounts/mfa/verify-setup/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token: verificationToken })
    });

    if (response.ok) {
      setSetupComplete(true);
      alert('MFA erfolgreich aktiviert!');
    } else {
      alert('Ungültiger Code. Bitte erneut versuchen.');
    }
  };

  return (
    <div>
      {!qrCode && (
        <button onClick={enableMFA}>MFA aktivieren</button>
      )}

      {qrCode && !setupComplete && (
        <div>
          <h2>QR-Code scannen</h2>
          <img src={qrCode} alt="MFA QR Code" />
          
          <h3>Backup-Codes (sicher speichern!)</h3>
          <ul>
            {backupCodes.map((code, index) => (
              <li key={index}>{code}</li>
            ))}
          </ul>

          <h3>Code eingeben</h3>
          <input
            type="text"
            placeholder="6-stelliger Code"
            value={verificationToken}
            onChange={(e) => setVerificationToken(e.target.value)}
            maxLength={6}
          />
          <button onClick={verifySetup}>Verifizieren</button>
        </div>
      )}

      {setupComplete && (
        <div>
          <h2>✅ MFA ist aktiviert</h2>
          <p>Ihr Account ist jetzt durch Zwei-Faktor-Authentifizierung geschützt.</p>
        </div>
      )}
    </div>
  );
}

export default MFASetup;
```

---

### React Beispiel - Login mit MFA

```jsx
import React, { useState } from 'react';

function LoginWithMFA() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [mfaRequired, setMfaRequired] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    const body = { 
      username: email, 
      password: password 
    };

    // Wenn MFA-Token vorhanden, mitschicken
    if (mfaToken) {
      body.mfa_token = mfaToken;
    }

    const response = await fetch('http://localhost:8000/api/accounts/login/', {
      method: 'POST',
      headers: {
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    const data = await response.json();

    if (data.mfa_required) {
      // MFA ist aktiviert - zeige MFA-Eingabefeld
      setMfaRequired(true);
    } else if (data.access) {
      // Login erfolgreich - Tokens speichern
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/dashboard';
    } else {
      alert('Login fehlgeschlagen');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={mfaRequired}
      />
      
      <input
        type="password"
        placeholder="Passwort"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={mfaRequired}
      />

      {mfaRequired && (
        <div>
          <p>🔒 Bitte geben Sie Ihren 6-stelligen MFA-Code ein:</p>
          <input
            type="text"
            placeholder="123456"
            value={mfaToken}
            onChange={(e) => setMfaToken(e.target.value)}
            maxLength={6}
            autoFocus
          />
          <p><small>Oder verwenden Sie einen Backup-Code</small></p>
        </div>
      )}

      <button type="submit">
        {mfaRequired ? 'Code verifizieren' : 'Anmelden'}
      </button>
    </form>
  );
}

export default LoginWithMFA;
```

---

## Authenticator-Apps

### Empfohlene Apps:

1. **Google Authenticator**
   - iOS: https://apps.apple.com/app/google-authenticator/id388497605
   - Android: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2

2. **Microsoft Authenticator**
   - iOS: https://apps.apple.com/app/microsoft-authenticator/id983156458
   - Android: https://play.google.com/store/apps/details?id=com.azure.authenticator

3. **Authy**
   - iOS: https://apps.apple.com/app/authy/id494168017
   - Android: https://play.google.com/store/apps/details?id=com.authy.authy

4. **1Password** (mit Authenticator-Funktion)
   - Alle Plattformen: https://1password.com/

---

## Technische Details

### TOTP-Spezifikationen

- **Algorithmus:** HMAC-SHA1
- **Zeitfenster:** 30 Sekunden
- **Code-Länge:** 6 Ziffern
- **Toleranz:** ±1 Zeitfenster (90 Sekunden Gesamt)

### Backup-Codes

- **Anzahl:** 10 Codes pro Generierung
- **Format:** 8-stellige Hexadezimal-Codes (A-F, 0-9)
- **Verwendung:** Einmalig (nach Verwendung ungültig)
- **Speicherung:** JSON-kodiert in Datenbank

### Sicherheitsmerkmale

1. **Secret Key Schutz**
   - Base32-kodiert
   - 32 Zeichen lang
   - Nur einmal bei Einrichtung angezeigt

2. **Deaktivierung erfordert:**
   - Aktuelles Passwort
   - Gültigen MFA-Token
   - Verhindert unbefugte Deaktivierung

3. **Admin-Interface:**
   - Secret-Preview (erste 8 + letzte 4 Zeichen)
   - Backup-Code-Zähler
   - Aktivierungsstatus
   - Nutzungsstatistiken

---

## Admin-Panel

### MFA-Geräte verwalten

Im Django Admin-Panel unter **MFA Devices** können Administratoren:

- MFA-Status aller Benutzer einsehen
- Verbleibende Backup-Codes anzeigen
- Letzten Verwendungszeitpunkt sehen
- MFA für Benutzer deaktivieren (Notfall)
- Aktivierungszeitpunkte überprüfen

**Felder:**
- Benutzer
- Status (Aktiv/Inaktiv)
- Secret (Vorschau)
- Erstellt am
- Aktiviert am
- Zuletzt verwendet
- Backup-Codes verbleibend

---

## Troubleshooting

### Problem: "Invalid token" beim Setup

**Lösung:**
1. Systemzeit auf Gerät und Server synchronisieren
2. QR-Code erneut scannen (alten Eintrag löschen)
3. Manuellen Key verwenden statt QR-Code
4. Anderen Authenticator probieren

### Problem: Backup-Code funktioniert nicht

**Lösung:**
1. Code ohne Leerzeichen/Bindestriche eingeben
2. Groß-/Kleinschreibung beachten
3. Code wurde bereits verwendet (einmalig)
4. Neue Backup-Codes generieren (mit MFA-Token)

### Problem: Gerät verloren, kein Backup-Code

**Lösung:**
1. Admin kontaktieren
2. Admin deaktiviert MFA im Admin-Panel
3. Erneutes Login ohne MFA möglich
4. MFA neu einrichten mit neuem Gerät

### Problem: Zeit-Synchronisation

**MFA basiert auf Zeit-Synchronisation zwischen Server und Gerät.**

**Lösung:**
1. Automatische Zeitzone auf Gerät aktivieren
2. NTP-Synchronisation auf Server prüfen
3. Toleranzfenster berücksichtigt ±30 Sekunden

---

## Best Practices

### Für Endbenutzer:

1. **Backup-Codes sicher speichern**
   - Ausdrucken und an sicherem Ort aufbewahren
   - In Passwort-Manager speichern
   - NICHT im selben Gerät wie Authenticator

2. **Mehrere Geräte einrichten**
   - Secret Key auch auf zweitem Gerät scannen
   - Redundanz für Notfälle

3. **Regelmäßige Tests**
   - Login mit MFA testen
   - Backup-Code-Funktion prüfen

### Für Entwickler:

1. **Rate Limiting implementieren**
   - Max. 5 Fehlversuche pro 15 Minuten
   - Schutz vor Brute-Force

2. **Logging aktivieren**
   - MFA-Aktivierungen protokollieren
   - Fehlgeschlagene Versuche loggen
   - Backup-Code-Verwendung tracken

3. **Email-Benachrichtigungen**
   - Bei MFA-Aktivierung
   - Bei MFA-Deaktivierung
   - Bei Backup-Code-Verwendung

---

## Konfiguration (Optional)

In `settings.py` können Sie folgende Einstellungen anpassen:

```python
# MFA Configuration (Optional)
MFA_ISSUER_NAME = 'Meine App Name'  # Name in Authenticator-App
MFA_TOKEN_VALIDITY_WINDOW = 1       # Zeitfenster-Toleranz (Standard: 1 = ±30 Sek.)
MFA_BACKUP_CODES_COUNT = 10         # Anzahl Backup-Codes
```

---

## Datenbankmodell

### MFADevice

```python
class MFADevice(models.Model):
    id = UUIDField(primary_key=True)
    user = OneToOneField(User)          # Ein Gerät pro Benutzer
    secret_key = CharField(max_length=32)  # Base32 TOTP Secret
    is_active = BooleanField()          # MFA aktiviert?
    backup_codes = TextField()          # JSON-Array
    created_at = DateTimeField()
    activated_at = DateTimeField()
    last_used = DateTimeField()
```

---

## Testing

### Manueller Test

1. **MFA aktivieren:**
   ```bash
   curl -X POST http://localhost:8000/api/accounts/mfa/enable/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **QR-Code scannen** mit Google Authenticator

3. **Setup verifizieren:**
   ```bash
   curl -X POST http://localhost:8000/api/accounts/mfa/verify-setup/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"token": "123456"}'
   ```

4. **Login mit MFA testen:**
   ```bash
   curl -X POST http://localhost:8000/api/accounts/login/ \
     -d '{"username": "user@example.com", "password": "pass", "mfa_token": "123456"}'
   ```

---

## Migration von bestehendem System

Wenn Sie bereits Benutzer haben und MFA hinzufügen:

1. **Opt-in Ansatz:** MFA ist optional (empfohlen)
2. **Benutzer informieren:** Email über neue Sicherheitsfunktion
3. **Anleitung bereitstellen:** Link zu MFA-Setup-Seite
4. **Admin-Accounts zuerst:** Administratoren aktivieren MFA
5. **Schrittweise Einführung:** Nach und nach für alle Benutzer

---

## Sicherheitsüberlegungen

### Was MFA schützt:

✅ Gestohlene Passwörter
✅ Phishing-Angriffe
✅ Brute-Force-Angriffe
✅ Credential Stuffing
✅ Datenbank-Leaks

### Was MFA NICHT schützt:

❌ Session Hijacking (HTTPS verwenden!)
❌ XSS-Angriffe (Input Sanitization!)
❌ Malware auf Gerät
❌ Social Engineering des Supports

### Zusätzliche Sicherheitsmaßnahmen:

1. HTTPS erzwingen
2. Secure & HttpOnly Cookies
3. CSRF-Schutz
4. Rate Limiting
5. IP-Whitelisting (optional)
6. Device Fingerprinting (optional)

---

## Support

Bei Fragen oder Problemen:

1. **Dokumentation prüfen:** Dieses Dokument
2. **Admin kontaktieren:** Bei Geräte-Verlust
3. **GitHub Issues:** Für Bugs und Feature-Requests

---

**Stand:** Dezember 2025
**Version:** 1.0
**Autor:** Auth Service Team
