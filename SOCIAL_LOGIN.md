# Social Login & Konfigurierbare Registrierung

## 🎯 Neue Features

### 1. Konfigurierbare Pflichtfelder bei Registrierung

Jede Website kann individuell festlegen, welche Informationen bei der Registrierung erforderlich sind.

#### Verfügbare Felder:
- ✅ **Vorname** (`require_first_name`)
- ✅ **Nachname** (`require_last_name`)
- ✅ **Telefon** (`require_phone`)
- ✅ **Adresse** (`require_address`) - Straße, Hausnummer, PLZ, Stadt, Land
- ✅ **Geburtsdatum** (`require_date_of_birth`)
- ✅ **Firma** (`require_company`)

#### Im Admin konfigurieren:

1. Gehe zu **Admin** → **Websites** → Deine Website bearbeiten
2. Unter **"Pflichtfelder bei Registrierung"** kannst du auswählen:
   - ☑️ Vorname erforderlich
   - ☑️ Nachname erforderlich
   - ☑️ Telefon erforderlich
   - ☑️ Adresse erforderlich
   - ☑️ Geburtsdatum erforderlich
   - ☑️ Firma erforderlich

#### API Endpoint:

```http
GET /api/accounts/websites/{website_id}/required-fields/
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Meine Website",
  "domain": "example.com",
  "require_first_name": true,
  "require_last_name": true,
  "require_phone": false,
  "require_address": true,
  "require_date_of_birth": false,
  "require_company": false
}
```

### 2. Social Login (Google, Facebook, GitHub, etc.)

#### Unterstützte Provider:
- 🔵 **Google**
- 🔵 **Facebook**
- 🔵 **GitHub**
- 🔵 **Microsoft**
- 🔵 **Apple**

#### Social Login API:

```http
POST /api/accounts/social-login/
```

**Request Body:**
```json
{
  "provider": "google",
  "provider_user_id": "1234567890",
  "email": "user@example.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  "avatar_url": "https://lh3.googleusercontent.com/..."
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user",
    "first_name": "Max",
    "last_name": "Mustermann",
    "profile_completed": false,
    ...
  },
  "social_account": {
    "id": "uuid",
    "provider": "google",
    "provider_display": "Google",
    "email": "user@example.com"
  },
  "tokens": {
    "access": "eyJ0eXAi...",
    "refresh": "eyJ0eXAi..."
  },
  "created": true,
  "profile_completed": false,
  "message": "Erfolgreich mit Social Login angemeldet."
}
```

### 3. Profil-Vervollständigung

Wenn ein Benutzer sich über Social Login anmeldet, können bestimmte Felder fehlen, die von der Website gefordert werden.

#### Profil auf Vollständigkeit prüfen:

```http
POST /api/accounts/check-profile-completion/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "website_id": "uuid"
}
```

**Response:**
```json
{
  "profile_completed": false,
  "missing_fields": [
    "phone",
    "street",
    "city",
    "postal_code"
  ],
  "required_fields": {
    "require_first_name": true,
    "require_last_name": true,
    "require_phone": true,
    "require_address": true,
    "require_date_of_birth": false,
    "require_company": false
  },
  "user": { ... }
}
```

#### Profil vervollständigen:

```http
POST /api/accounts/complete-profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "website_id": "uuid",
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "profile_completed": true,
    ...
  },
  "message": "Profil erfolgreich vervollständigt."
}
```

### 4. Social Accounts verwalten

#### Alle verlinkten Social Accounts anzeigen:

```http
GET /api/accounts/social-accounts/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "social_accounts": [
    {
      "id": "uuid",
      "provider": "google",
      "provider_display": "Google",
      "email": "user@gmail.com",
      "first_name": "Max",
      "last_name": "Mustermann",
      "avatar_url": "https://...",
      "created_at": "2025-12-22T13:00:00Z"
    },
    {
      "id": "uuid",
      "provider": "github",
      "provider_display": "GitHub",
      "email": "user@users.noreply.github.com",
      ...
    }
  ]
}
```

#### Social Account entfernen:

```http
DELETE /api/accounts/social-accounts/{provider}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "google Account erfolgreich entfernt."
}
```

## 📱 Integration Beispiele

### JavaScript/React - Social Login mit Google

```javascript
import { authClient } from './auth-client';

// 1. Google OAuth initiieren (Frontend)
async function loginWithGoogle() {
  // Verwende Google OAuth Library oder Firebase Auth
  const googleUser = await signInWithGoogle();
  
  // 2. An Auth Service senden
  const response = await authClient.socialLogin({
    provider: 'google',
    provider_user_id: googleUser.uid,
    email: googleUser.email,
    first_name: googleUser.displayName?.split(' ')[0] || '',
    last_name: googleUser.displayName?.split(' ')[1] || '',
    avatar_url: googleUser.photoURL || ''
  });
  
  // 3. Prüfe ob Profil vollständig ist
  if (!response.profile_completed) {
    // Zeige Formular für fehlende Daten
    const missing = await authClient.checkProfileCompletion(websiteId);
    showCompleteProfileForm(missing.missing_fields);
  } else {
    // Weiterleitung zur App
    redirectToApp();
  }
}

// 4. Profil vervollständigen
async function completeProfile(data) {
  await authClient.completeProfile({
    website_id: websiteId,
    ...data
  });
  
  redirectToApp();
}
```

### Erweiterte JavaScript Client Methoden

```javascript
class AuthServiceClient {
  // ... existing methods ...
  
  async socialLogin(data) {
    return this.request('/api/accounts/social-login/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  async checkProfileCompletion(websiteId) {
    return this.request('/api/accounts/check-profile-completion/', {
      method: 'POST',
      body: JSON.stringify({ website_id: websiteId })
    });
  }
  
  async completeProfile(data) {
    return this.request('/api/accounts/complete-profile/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  async getSocialAccounts() {
    return this.request('/api/accounts/social-accounts/');
  }
  
  async unlinkSocialAccount(provider) {
    return this.request(`/api/accounts/social-accounts/${provider}/`, {
      method: 'DELETE'
    });
  }
  
  async getWebsiteRequiredFields(websiteId) {
    return this.request(`/api/accounts/websites/${websiteId}/required-fields/`);
  }
}
```

### React Komponente - Profil-Vervollständigung

```jsx
import React, { useState, useEffect } from 'react';
import { authClient } from './auth-client';

function CompleteProfileForm({ websiteId, onComplete }) {
  const [missingFields, setMissingFields] = useState([]);
  const [formData, setFormData] = useState({});
  
  useEffect(() => {
    loadRequiredFields();
  }, []);
  
  async function loadRequiredFields() {
    const result = await authClient.checkProfileCompletion(websiteId);
    setMissingFields(result.missing_fields);
  }
  
  async function handleSubmit(e) {
    e.preventDefault();
    
    await authClient.completeProfile({
      website_id: websiteId,
      ...formData
    });
    
    onComplete();
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Bitte vervollständige dein Profil</h2>
      
      {missingFields.includes('phone') && (
        <input
          type="tel"
          placeholder="Telefonnummer"
          value={formData.phone || ''}
          onChange={(e) => setFormData({...formData, phone: e.target.value})}
          required
        />
      )}
      
      {missingFields.includes('street') && (
        <>
          <input
            type="text"
            placeholder="Straße"
            value={formData.street || ''}
            onChange={(e) => setFormData({...formData, street: e.target.value})}
            required
          />
          <input
            type="text"
            placeholder="Hausnummer"
            value={formData.street_number || ''}
            onChange={(e) => setFormData({...formData, street_number: e.target.value})}
            required
          />
        </>
      )}
      
      {missingFields.includes('city') && (
        <input
          type="text"
          placeholder="Stadt"
          value={formData.city || ''}
          onChange={(e) => setFormData({...formData, city: e.target.value})}
          required
        />
      )}
      
      {missingFields.includes('postal_code') && (
        <input
          type="text"
          placeholder="PLZ"
          value={formData.postal_code || ''}
          onChange={(e) => setFormData({...formData, postal_code: e.target.value})}
          required
        />
      )}
      
      {missingFields.includes('country') && (
        <input
          type="text"
          placeholder="Land"
          value={formData.country || ''}
          onChange={(e) => setFormData({...formData, country: e.target.value})}
          required
        />
      )}
      
      {missingFields.includes('date_of_birth') && (
        <input
          type="date"
          value={formData.date_of_birth || ''}
          onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
          required
        />
      )}
      
      {missingFields.includes('company') && (
        <input
          type="text"
          placeholder="Firma"
          value={formData.company || ''}
          onChange={(e) => setFormData({...formData, company: e.target.value})}
          required
        />
      )}
      
      <button type="submit">Profil vervollständigen</button>
    </form>
  );
}
```

## 🔧 Workflow

### Typischer Ablauf mit Social Login:

1. **Benutzer klickt auf "Mit Google anmelden"**
   - Frontend initiiert Google OAuth
   - Erhält Benutzerdaten von Google

2. **Frontend sendet Daten an Auth Service**
   ```javascript
   POST /api/accounts/social-login/
   ```

3. **Auth Service erstellt/findet Benutzer**
   - Neuer Benutzer → Account wird erstellt
   - Existierender Benutzer → Social Account wird verknüpft
   - JWT Tokens werden generiert

4. **Frontend prüft Profil-Vollständigkeit**
   ```javascript
   POST /api/accounts/check-profile-completion/
   ```

5. **Falls unvollständig → Zeige Formular**
   - Nur fehlende Pflichtfelder werden abgefragt
   - Basierend auf Website-Konfiguration

6. **Benutzer ergänzt Daten**
   ```javascript
   POST /api/accounts/complete-profile/
   ```

7. **Weiterleitung zur App**
   - Profil vollständig ✅
   - Alle Tokens vorhanden ✅

## 🎨 Best Practices

### 1. **Initialer Social Login Check**
```javascript
if (!response.profile_completed) {
  // Speichere Token trotzdem
  localStorage.setItem('access_token', response.tokens.access);
  
  // Zeige Vervollständigungs-Formular
  showCompleteProfileModal();
} else {
  // Direkt einloggen
  redirectToApp();
}
```

### 2. **Website-spezifische Anforderungen abfragen**
```javascript
// Beim Laden der Registrierungsseite
const requiredFields = await authClient.getWebsiteRequiredFields(websiteId);
// Zeige nur relevante Felder im Formular
```

### 3. **Graceful Fallback**
```javascript
try {
  await authClient.socialLogin(data);
} catch (error) {
  // Fallback zu normaler Registrierung
  showEmailPasswordForm();
}
```

## 📋 Checkliste für Website-Admin

- [ ] Website im Admin-Interface registrieren
- [ ] Pflichtfelder konfigurieren (Adresse, Telefon, etc.)
- [ ] Social Login Provider konfigurieren (in deiner App)
- [ ] Frontend Integration testen
- [ ] Profil-Vervollständigung UI implementieren
- [ ] Error Handling für fehlende Daten

---

**Viel Erfolg mit Social Login & konfigurierbarer Registrierung! 🚀**
