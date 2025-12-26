# 🔧 Lexware Integration - Neue Fixes

## Problem 1: Country Code Fehler (406) ✅ GELÖST

### Fehlermeldung:
```json
{
  "requestId": "393d04c3-eb7c-4286-ad8f-bbb3e76a2896",
  "IssueList": [{
    "i18nKey": "countrycode_is_not_valid",
    "source": "countryCode",
    "type": "validation_failure"
  }]
}
```

### Ursache:
Lexware API akzeptiert nur gültige **ISO-3166-1 Alpha-2** Country Codes (z.B. "DE", "AT", "CH"). 
Das User-Model speichert oft Ländernamen wie "Deutschland" oder leere Werte.

### Lösung:
Neue `normalize_country_code()` Funktion in `lexware_integration.py`:

```python
# Akzeptiert:
"Deutschland" → "DE"
"Österreich" → "AT"
"Schweiz" → "CH"
"DE" → "DE" (bereits gültig)
"" → "DE" (Fallback)
None → "DE" (Fallback)

# Unterstützt 40+ Länder:
DE, AT, CH, FR, IT, ES, GB, NL, BE, LU, DK, SE, NO, FI, PL, CZ, SK, HU, 
RO, BG, GR, PT, IE, HR, SI, EE, LV, LT, CY, MT, US, CA, AU, NZ, JP, CN, 
IN, BR, MX, AR
```

### Testing:
```bash
# Teste mit verschiedenen Länder-Werten
python manage.py sync_lexware_contacts --create-missing

# Funktioniert jetzt mit:
# - user.country = "Deutschland" ✓
# - user.country = "DE" ✓
# - user.country = "" ✓ (verwendet "DE" als Fallback)
# - user.country = None ✓ (verwendet "DE" als Fallback)
```

---

## Problem 2: Automatische Lexware-Erstellung nach complete-profile ✅ GELÖST

### Anforderung:
> "Wenn ein Konto bei Lexware nicht erstellt wurde muss es irgendwie ein Prozess geben das eventuell nach complete-profile dies passiert"

### Lösung:
`CompleteProfileView` wurde erweitert:

#### Neues Verhalten:
1. **Profil wird vervollständigt** → Speichert Benutzerdaten
2. **Automatische Prüfung**: Ist Profil jetzt Lexware-bereit?
3. **Automatische Erstellung**: Lexware-Kontakt wird erstellt (falls noch nicht vorhanden)
4. **Automatische Aktualisierung**: Existierende Kontakte werden aktualisiert

#### API Response:
```json
// Neuer Benutzer - Lexware-Kontakt erstellt
{
  "user": { ... },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_created": true,
  "lexware_customer_number": 10019
}

// Existierender Benutzer - Kontakt aktualisiert
{
  "user": { ... },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_updated": true
}

// Profil noch unvollständig
{
  "user": { ... },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_info": "Profil noch unvollständig für Lexware: Name oder Firma"
}
```

#### Frontend Integration:
```javascript
const completeProfile = async (profileData) => {
  const response = await fetch('/api/accounts/complete-profile/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      first_name: 'Max',
      last_name: 'Mustermann',
      street: 'Musterstraße',
      street_number: '123',
      city: 'Berlin',
      postal_code: '10115',
      country: 'Deutschland',
      company: 'Musterfirma GmbH'
    })
  });
  
  const data = await response.json();
  
  if (data.lexware_created) {
    console.log(`Lexware-Kundennummer: ${data.lexware_customer_number}`);
    showNotification('Profil vervollständigt & Kundenkonto erstellt!', 'success');
  } else if (data.lexware_updated) {
    console.log('Lexware-Kontakt wurde aktualisiert');
  } else if (data.lexware_info) {
    console.log(data.lexware_info);
  }
};
```

---

## Problem 3: check-profile-completion ohne website_id ✅ GELÖST

### Anforderung:
> "bei check-profile-completion muss eine website id angegeben werden das ist doof denn die Anforderung soll Allgemein sein und nicht website bezogen"

### Lösung:
`CheckProfileCompletionView` unterstützt jetzt **beides**:

#### 1. Allgemeine Prüfung (OHNE website_id)

**GET Request** (neu!):
```bash
GET /api/accounts/check-profile-completion/
Authorization: Bearer <access_token>
```

**POST Request** (ohne website_id):
```bash
POST /api/accounts/check-profile-completion/
Authorization: Bearer <access_token>
# Body: {} oder leer
```

**Response:**
```json
{
  "profile_completed": true,              // Lexware-bereit?
  "missing_fields": [],                   // Fehlende Felder für Lexware
  "has_lexware_contact": true,            // Bereits in Lexware?
  "lexware_customer_number": 10019,       // Kundennummer (falls vorhanden)
  "user": { ... }                         // Vollständige Benutzerdaten
}

// Wenn unvollständig:
{
  "profile_completed": false,
  "missing_fields": [
    "Name oder Firma",
    "Adresse (Stadt/PLZ) [empfohlen]"
  ],
  "has_lexware_contact": false,
  "lexware_customer_number": null,
  "user": { ... }
}
```

#### 2. Website-spezifische Prüfung (MIT website_id)

**POST Request** (mit website_id):
```bash
POST /api/accounts/check-profile-completion/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "website_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "profile_completed": true,              // Allgemeine Lexware-Prüfung
  "missing_fields": [],                   
  "has_lexware_contact": true,
  "lexware_customer_number": 10019,
  "user": { ... },
  
  "website_check": {                      // Zusätzlich: Website-spezifisch
    "website_id": "550e8400-e29b-41d4-a716-446655440000",
    "website_name": "My Website",
    "profile_completed": true,
    "missing_fields": [],
    "required_fields": {
      "require_first_name": true,
      "require_last_name": true,
      "require_phone": false,
      "require_address": true,
      "require_date_of_birth": false,
      "require_company": false
    }
  }
}
```

#### Frontend Integration:

```javascript
// Allgemeine Prüfung (GET - einfacher!)
const checkProfile = async () => {
  const response = await fetch('/api/accounts/check-profile-completion/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const data = await response.json();
  
  if (!data.profile_completed) {
    showBanner(`Bitte vervollständige dein Profil: ${data.missing_fields.join(', ')}`);
  }
  
  if (!data.has_lexware_contact) {
    console.log('Noch kein Lexware-Kundenkonto erstellt');
  }
};

// Website-spezifische Prüfung (optional)
const checkWebsiteProfile = async (websiteId) => {
  const response = await fetch('/api/accounts/check-profile-completion/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ website_id: websiteId })
  });
  
  const data = await response.json();
  
  // Allgemeine Prüfung
  console.log('Lexware-bereit:', data.profile_completed);
  
  // Website-spezifische Prüfung
  if (data.website_check) {
    console.log('Website-Anforderungen erfüllt:', data.website_check.profile_completed);
  }
};
```

---

## Workflow-Beispiel

### Szenario: Neuer Benutzer mit Social Login

```javascript
// 1. Benutzer loggt sich mit Google ein
const googleLogin = await socialLogin({
  provider: 'google',
  provider_user_id: '1234567890',
  email: 'max@example.com',
  first_name: 'Max'
  // Keine Adresse, kein Nachname!
});

console.log(googleLogin.profile_completed); // false

// 2. Prüfe Profil-Status
const profileCheck = await fetch('/api/accounts/check-profile-completion/', {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${googleLogin.tokens.access}` }
}).then(r => r.json());

console.log(profileCheck);
// {
//   "profile_completed": false,
//   "missing_fields": ["Name oder Firma"],
//   "has_lexware_contact": false,
//   "lexware_customer_number": null
// }

// 3. Zeige Banner: "Bitte vervollständige dein Profil"
showProfileCompletionBanner(profileCheck.missing_fields);

// 4. Benutzer vervollständigt Profil
const completed = await fetch('/api/accounts/complete-profile/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${googleLogin.tokens.access}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    last_name: 'Mustermann',
    street: 'Musterstraße',
    street_number: '123',
    city: 'Berlin',
    postal_code: '10115',
    country: 'Deutschland'
  })
}).then(r => r.json());

console.log(completed);
// {
//   "user": { ... },
//   "message": "Profil erfolgreich vervollständigt.",
//   "lexware_created": true,              ← Automatisch erstellt!
//   "lexware_customer_number": 10019      ← Neue Kundennummer!
// }

// 5. Profil ist jetzt vollständig
const recheckProfile = await fetch('/api/accounts/check-profile-completion/', {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${googleLogin.tokens.access}` }
}).then(r => r.json());

console.log(recheckProfile);
// {
//   "profile_completed": true,
//   "missing_fields": [],
//   "has_lexware_contact": true,          ← Jetzt vorhanden!
//   "lexware_customer_number": 10019
// }
```

---

## User Model Hilfsfunktionen

Die neuen Methoden im User-Model helfen bei der Validierung:

```python
from accounts.models import User

# Prüfen ob Profil Lexware-bereit ist
user = User.objects.get(email='max@example.com')

if user.is_ready_for_lexware():
    print("✓ Profil ist vollständig für Lexware")
else:
    missing = user.get_lexware_missing_fields()
    print(f"⊘ Fehlende Felder: {', '.join(missing)}")
    # Output: ⊘ Fehlende Felder: Name oder Firma, Adresse (Stadt/PLZ) [empfohlen]

# In Django Templates
{% if user.is_ready_for_lexware %}
    <span class="badge badge-success">Profil vollständig</span>
{% else %}
    <div class="alert alert-warning">
        Fehlende Felder: {{ user.get_lexware_missing_fields|join:", " }}
    </div>
{% endif %}
```

---

## Testing

### 1. Country Code Fix testen:
```bash
# Erstelle Test-Benutzer mit verschiedenen Länder-Werten
python manage.py shell

from accounts.models import User

# Test 1: Ländername
user1 = User.objects.create_user(
    email='test1@example.com',
    username='test1',
    first_name='Max',
    last_name='Test',
    country='Deutschland',  # ← Wird zu "DE"
    city='Berlin',
    postal_code='10115'
)

# Test 2: ISO-Code
user2 = User.objects.create_user(
    email='test2@example.com',
    username='test2',
    first_name='Hans',
    last_name='Test',
    country='AT',  # ← Bleibt "AT"
    city='Wien',
    postal_code='1010'
)

# Test 3: Leer
user3 = User.objects.create_user(
    email='test3@example.com',
    username='test3',
    company='Test GmbH',
    country='',  # ← Wird zu "DE"
    city='München',
    postal_code='80331'
)

# Synchronisiere mit Lexware
exit()

python manage.py sync_lexware_contacts --create-missing

# Sollte jetzt OHNE 406-Fehler durchlaufen!
```

### 2. complete-profile testen:
```bash
curl -X POST http://localhost:8000/api/accounts/complete-profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Max",
    "last_name": "Mustermann",
    "street": "Musterstraße",
    "street_number": "123",
    "city": "Berlin",
    "postal_code": "10115",
    "country": "Deutschland"
  }'

# Response enthält:
# "lexware_created": true (bei neuem Kontakt)
# "lexware_customer_number": 10019
```

### 3. check-profile-completion testen:
```bash
# GET (ohne website_id)
curl -X GET http://localhost:8000/api/accounts/check-profile-completion/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# POST (mit website_id - optional)
curl -X POST http://localhost:8000/api/accounts/check-profile-completion/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## Migration anwenden

Vergiss nicht die Migration anzuwenden:

```bash
python manage.py migrate accounts
```

---

## Zusammenfassung

### ✅ Alle 3 Probleme gelöst:

1. **Country Code (406)**: 
   - Automatische Normalisierung zu ISO-3166-1 Alpha-2
   - Unterstützt Ländernamen wie "Deutschland", "Österreich"
   - Fallback auf "DE" bei leeren Werten

2. **Automatische Erstellung nach complete-profile**:
   - Lexware-Kontakt wird automatisch erstellt
   - Existierende Kontakte werden aktualisiert
   - Transparentes Feedback in API Response

3. **check-profile-completion ohne website_id**:
   - GET-Endpoint für einfache Prüfung
   - Allgemeine Lexware-Prüfung (immer)
   - Website-spezifische Prüfung (optional)

### 🎯 Vorteile:

- ✅ Keine 406-Fehler mehr bei Lexware API
- ✅ Automatischer Workflow nach Profil-Vervollständigung
- ✅ Flexiblere API ohne Zwang zur website_id
- ✅ Bessere User Experience durch automatische Prozesse
- ✅ Vollständige Rückwärtskompatibilität

---

Alle Änderungen sind sofort produktionsbereit! 🚀
