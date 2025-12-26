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
  "lexware_ready": false,
  "lexware_missing_fields": ["Straße", "Stadt", "PLZ"],
  "lexware_info": "Profil unvollständig für Kundenkonto. Fehlende Felder: Straße, Stadt, PLZ",
  "message": "Erfolgreich mit Social Login angemeldet."
}
```

### 3. Profil-Vervollständigung (inkl. Lexware-Kundenkonto)

Wenn ein Benutzer sich über Social Login anmeldet, können bestimmte Felder fehlen, die von der Website gefordert werden **oder für ein Lexware-Kundenkonto benötigt werden**.

#### Wichtig: Lexware-Kundenkonto Anforderungen

Ein Lexware-Kundenkonto wird **nur** erstellt, wenn folgende Daten vorhanden sind:
- ✅ E-Mail
- ✅ Vorname **UND** Nachname
- ✅ Vollständige Adresse (Straße, Stadt, PLZ)

# Allgemeine Prüfung (ohne website_id) - prüft Lexware-Bereitschaft
{}

# ODER mit website_id für website-spezifische Prüfung
{
  "website_id": "uuid"
}
```

**Response (allgemein):**
```json
{
  "profile_completed": false,
  "missing_fields": ["Straße", "Stadt", "PLZ"],
  "has_lexware_contact": false,
  "lexware_customer_number": null,
  "user": { ... }
}
```

**Response (mit website_id):**
```json
{
  "profile_completed": false,
  "missing_fields": ["Straße", "Stadt", "PLZ"],
  "has_lexware_contact": false,
  "lexware_customer_number": null,
  "user": { ... },
  "website_check": {
    "website_id": "uuid",
    "website_name": "Meine Website",
    "profile_completed": false,
    "missing_fields": [
      "phone",
      "street",
      "city",
      "postal_code" (erstellt automatisch Lexware-Kontakt):

```http
POST /api/accounts/complete-profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "phone": "+49123456789",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland"
}
```

**Response (mit automatischer Lexware-Kontakt-Erstellung):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "profile_completed": true,
    "lexware_customer_number": 10020,
    ...
  },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_created": true,
  "lexware_customer_number": 10020
}
```

**Response (wenn Profil noch unvollständig):**
```json
{
  "user": { ... },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_info": "Profil noch unvollständig für Lexware: Straße, Stadt
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

### JavaScript/React - Social Login mit Google (inkl. Lexware)

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
  
  console.log('Login Response:', response);
  // {
  //   user: { ... },
  //   tokens: { ... },
  //   lexware_ready: false,
  //   lexware_missing_fields: ["Straße", "Stadt", "PLZ"],
  //   lexware_info: "Profil unvollständig für Kundenkonto. Fehlende Felder: Straße, Stadt, PLZ"
  // }
  
  // 3. Prüfe ob Profil vollständig ist
  if (!response.lexware_ready) {
    // Zeige Hinweis: Profil vervollständigen für Kundenkonto
    showCompleteProfileForm({
      message: response.lexware_info,
      missing_fields: response.lexware_missing_fields
    });
  } else {
    // Profil vollständig + Lexware-Kundenkonto vorhanden
    console.log(`Lexware Kundennummer: ${response.lexware_customer_number}`);
    redirectToApp();
  }
}

// 4. Profil vervollständigen (erstellt automatisch Lexware-Kontakt)
async function completeProfile(data) {
  const result = await authClient.completeProfile(data);
  
  if (result.lexware_created) {
    console.log(`✅ Kundenkonto erstellt! Kundennummer: ${result.lexware_customer_number}`);
    showSuccess('Profil vervollständigt & Kundenkonto erstellt!');
  } else if (result.lexware_info) {
    console.log(`⚠️ ${result.lexware_info}`);
    showWarning(result.lexware_info);
  }
  
  redirectToApp();
}
```

### Vollständiger Flow: Google Login → Profil vervollständigen → Lexware

```javascript
// Beispiel: Vollständiger Social Login Flow mit Lexware-Integration

async function handleGoogleLogin() {
  try {
    // Schritt 1: Google Login
    const googleUser = await signInWithGoogle();
    
    // Schritt 2: An Auth Service senden
    const authResponse = await fetch('http://localhost:8000/api/accounts/social-login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: 'google',
        provider_user_id: googleUser.uid,
        email: googleUser.email,
        first_name: googleUser.displayName?.split(' ')[0],
        last_name: googleUser.displayName?.split(' ')[1]
      })
    });
    
    const data = await authResponse.json();
    
    // Tokens speichern
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    
    // Schritt 3: Lexware-Bereitschaft prüfen
    if (!data.lexware_ready) {
      console.log('📝 Profil unvollständig:', data.lexware_missing_fields);
      
      // Zeige Formular
      const formData = await showAddressForm({
        title: 'Vervollständige dein Profil',
        subtitle: 'Für dein Kundenkonto benötigen wir noch deine Adresse',
        fields: data.lexware_missing_fields
      });
      
      // Schritt 4: Profil vervollständigen
      const completeResponse = await fetch('http://localhost:8000/api/accounts/complete-profile/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${data.tokens.access}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          street: formData.street,
          street_number: formData.streetNumber,
          city: formData.city,
          postal_code: formData.postalCode,
          country: formData.country || 'Deutschland'
        })
      });
      
      const completeData = await completeResponse.json();
      
      if (completeData.lexware_created) {
        console.log(`✅ Kundenkonto erstellt! Kundennummer: ${completeData.lexware_customer_number}`);
        showNotification('success', 'Profil vervollständigt & Kundenkonto erstellt!');
      }
    } else {
      console.log(`✅ Bereits vollständiges Profil. Kundennummer: ${data.lexware_customer_number}`);
    }
    
    // Schritt 5: Weiterleitung
    window.location.href = '/dashboard';
    
  } catch (error) {
    console.error('❌ Login fehlgeschlagen:', error);
    showNotification('error', 'Login fehlgeschlagen. Bitte versuche es erneut.');
  }
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
  
  async checkProfileCompletion(websiteId = null) {
    const body = websiteId ? { website_id: websiteId } : {};
    return this.request('/api/accounts/check-profile-completion/', {
      method: websiteId ? 'POST' : 'GET',
      body: websiteId ? JSON.stringify(body) : undefined
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
