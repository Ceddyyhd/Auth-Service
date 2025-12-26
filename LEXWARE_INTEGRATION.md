# 🔗 Lexware API Integration für Auth-Service

## Übersicht

Diese Integration verbindet den Auth-Service automatisch mit der **Lexware API**, sodass bei jeder Benutzerregistrierung automatisch ein Kundenkonto in Lexware erstellt wird. Die eindeutige **Kundennummer** wird dann beim Benutzer im Auth-Service gespeichert.

## 📚 Dokumentation

Vollständige Lexware API Dokumentation: https://developers.lexware.io/docs/

## ✨ Features

- ✅ **Automatische Kundenerstellung**: Bei der Registrierung wird automatisch ein Lexware-Kontakt erstellt
- ✅ **Kundennummer-Speicherung**: Die Lexware-Kundennummer wird im User-Model gespeichert
- ✅ **Unterstützung für Privat- und Firmenkunden**: Unterschiedliche Kontakttypen basierend auf den Benutzerdaten
- ✅ **Fehlertoleranz**: Registrierung schlägt nicht fehl, wenn Lexware nicht erreichbar ist
- ✅ **Management Command**: Synchronisation bestehender Benutzer mit Lexware
- ✅ **API-Endpunkte**: Aktualisierung von Lexware-Kontakten bei Profil-Änderungen

## 🔧 Installation & Konfiguration

### 1. API Key erstellen

1. Melde dich bei Lexware an: https://app.lexware.de/
2. Gehe zu: **Einstellungen** → **Public API** (https://app.lexware.de/addons/public-api)
3. Klicke auf **"API-Schlüssel generieren"**
4. Kopiere den generierten API Key

### 2. Umgebungsvariablen konfigurieren

Füge den API Key zur `.env` Datei hinzu:

```env
# Lexware API Integration
LEXWARE_API_KEY=dein_api_key_hier
```

### 3. Django Settings aktualisieren

Die Settings sind bereits vorbereitet. In `settings.py` wird automatisch gelesen:

```python
# Lexware API Configuration
LEXWARE_API_KEY = config('LEXWARE_API_KEY', default=None)
```

### 4. Datenbank-Migration ausführen

```bash
python manage.py migrate accounts
```

Dies erstellt die neuen Felder:
- `lexware_contact_id` (UUID) - Die eindeutige ID des Kontakts in Lexware
- `lexware_customer_number` (Integer) - Die Kundennummer aus Lexware

## 🚀 Verwendung

### Bei der Registrierung

Wenn ein neuer Benutzer registriert wird, passiert automatisch Folgendes:

1. Benutzer wird im Auth-Service erstellt
2. JWT-Tokens werden generiert
3. **Lexware-Kontakt wird erstellt** (asynchron, blockiert nicht die Registrierung)
4. Kundennummer wird beim Benutzer gespeichert

**API Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user123",
    "lexware_contact_id": "lexware-uuid",
    "lexware_customer_number": 10001
  },
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  },
  "message": "Benutzer erfolgreich registriert.",
  "verification_email_sent": true,
  "lexware_customer_number": 10001
}
```

### Bestehende Benutzer synchronisieren

Um Lexware-Kontakte für bestehende Benutzer zu erstellen:

```bash
# Alle Benutzer ohne Lexware-Kontakt synchronisieren
python manage.py sync_lexware_contacts --create-missing

# Bestehende Lexware-Kontakte aktualisieren
python manage.py sync_lexware_contacts --update-existing

# Beides gleichzeitig
python manage.py sync_lexware_contacts --create-missing --update-existing

# Nur Test (Dry Run)
python manage.py sync_lexware_contacts --create-missing --dry-run

# Nur einen bestimmten Benutzer
python manage.py sync_lexware_contacts --create-missing --email user@example.com
```

**Ausgabe:**
```
Synchronisiere 42 Benutzer mit Lexware...

✓ Kontakt erstellt für user1@example.com (ID: uuid) - Kundennummer: 10001
✓ Kontakt erstellt für user2@example.com (ID: uuid) - Kundennummer: 10002
✗ Fehler beim Erstellen für user3@example.com: API Error

============================================================
Synchronisation abgeschlossen!

Gesamt:        42
Erstellt:      40
Aktualisiert:  0
Übersprungen:  0
Fehler:        2
============================================================
```

### Programmatische Verwendung

```python
from accounts.lexware_integration import get_lexware_client, LexwareAPIError

# Client-Instanz holen
lexware = get_lexware_client()

# Neuen Kontakt erstellen
try:
    contact = lexware.create_customer_contact(user)
    print(f"Kundennummer: {user.lexware_customer_number}")
except LexwareAPIError as e:
    print(f"Fehler: {e}")

# Kontakt aktualisieren
try:
    contact = lexware.update_customer_contact(user)
    print("Kontakt aktualisiert")
except LexwareAPIError as e:
    print(f"Fehler: {e}")

# Kontakt abrufen
contact = lexware.get_contact(user.lexware_contact_id)

# Nach E-Mail suchen
contacts = lexware.search_contacts_by_email("user@example.com")

# Kundennummer abrufen
customer_number = lexware.get_customer_number(user)
```

## 📋 Kontakt-Datenstruktur in Lexware

### Privatkunden

```json
{
  "version": 0,
  "roles": {
    "customer": {}
  },
  "person": {
    "firstName": "Max",
    "lastName": "Mustermann"
  },
  "addresses": {
    "billing": [{
      "street": "Musterstraße 123",
      "city": "Berlin",
      "zip": "10115",
      "countryCode": "DE"
    }]
  },
  "emailAddresses": {
    "private": ["max@example.com"]
  },
  "phoneNumbers": {
    "private": ["+49123456789"]
  },
  "note": "Automatisch erstellt über Auth-Service am 26.12.2025"
}
```

### Firmenkunden

```json
{
  "version": 0,
  "roles": {
    "customer": {}
  },
  "company": {
    "name": "Meine Firma GmbH",
    "contactPersons": [{
      "firstName": "Max",
      "lastName": "Mustermann",
      "primary": true,
      "emailAddress": "max@example.com",
      "phoneNumber": "+49123456789"
    }]
  },
  "addresses": {
    "billing": [{
      "street": "Musterstraße 123",
      "city": "Berlin",
      "zip": "10115",
      "countryCode": "DE"
    }]
  },
  "emailAddresses": {
    "business": ["max@example.com"]
  },
  "phoneNumbers": {
    "business": ["+49123456789"]
  },
  "note": "Automatisch erstellt über Auth-Service am 26.12.2025"
}
```

## 🔍 User-Model Felder

### Neue Felder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `lexware_contact_id` | UUIDField | UUID des Kontakts in Lexware (nullable) |
| `lexware_customer_number` | IntegerField | Eindeutige Kundennummer aus Lexware (nullable, unique) |

### Verwendete Felder für Kontakterstellung

| Auth-Service Feld | Lexware Feld | Bemerkung |
|-------------------|--------------|-----------|
| `company` | `company.name` | Wenn vorhanden → Firmenkunde |
| `first_name` | `person.firstName` / `contactPersons[0].firstName` | |
| `last_name` | `person.lastName` / `contactPersons[0].lastName` | |
| `email` | `emailAddresses.private` / `business` | |
| `phone` | `phoneNumbers.private` / `business` | |
| `street` + `street_number` | `addresses.billing[0].street` | |
| `city` | `addresses.billing[0].city` | |
| `postal_code` | `addresses.billing[0].zip` | |
| `country` | `addresses.billing[0].countryCode` | Standard: "DE" |

## ⚙️ Konfigurationsoptionen

### Rate Limits

Lexware API hat folgende Rate Limits:
- **2 Requests pro Sekunde** für alle Endpoints zusammen

Die Integration verwendet automatisches Error-Handling und Logging.

### Fehlerbehandlung

```python
try:
    contact = lexware.create_customer_contact(user)
except LexwareAPIError as e:
    # API-Fehler (HTTP-Fehler, Validierung, etc.)
    logger.error(f"Lexware API Error: {e}")
except Exception as e:
    # Andere Fehler (Konfiguration, Netzwerk, etc.)
    logger.warning(f"Unexpected error: {e}")
```

### Logging

Alle Lexware-Operationen werden geloggt:

```python
import logging
logger = logging.getLogger('accounts.lexware_integration')
```

Log-Level in `settings.py`:

```python
LOGGING = {
    'loggers': {
        'accounts.lexware_integration': {
            'level': 'INFO',  # oder 'DEBUG' für mehr Details
        },
    },
}
```

## 🧪 Testing

### Test-Account erstellen

```bash
# Lexware Test-Account: https://app.lexware.de/signup
# Kostenlos für 30 Tage mit allen Features
```

### Integration testen

```python
from django.test import TestCase
from accounts.models import User
from accounts.lexware_integration import get_lexware_client

class LexwareIntegrationTest(TestCase):
    def test_create_customer_contact(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            city='Berlin',
            postal_code='10115',
            country='DE'
        )
        
        lexware = get_lexware_client()
        contact = lexware.create_customer_contact(user)
        
        self.assertIsNotNone(user.lexware_contact_id)
        self.assertIsNotNone(user.lexware_customer_number)
        self.assertIsInstance(contact, dict)
```

## 📊 API-Endpunkte

### Lexware-Kontakt manuell erstellen

```python
# In views.py oder Custom Management Command
from accounts.lexware_integration import get_lexware_client

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lexware_contact(request):
    user = request.user
    if user.lexware_contact_id:
        return Response({
            'message': 'Lexware-Kontakt existiert bereits',
            'customer_number': user.lexware_customer_number
        })
    
    try:
        lexware = get_lexware_client()
        contact = lexware.create_customer_contact(user)
        return Response({
            'message': 'Lexware-Kontakt erstellt',
            'customer_number': user.lexware_customer_number,
            'contact_id': str(user.lexware_contact_id)
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## 🚨 Troubleshooting

### Fehler: "Lexware API Key nicht konfiguriert"

**Lösung:** Stelle sicher, dass `LEXWARE_API_KEY` in der `.env` Datei gesetzt ist.

### Fehler: "401 Unauthorized"

**Lösung:** API Key ist ungültig oder abgelaufen. Generiere einen neuen Key in Lexware.

### Fehler: "429 Too Many Requests"

**Lösung:** Rate Limit erreicht (2 Requests/Sekunde). Warte kurz und versuche es erneut.

### Kontakt wird nicht erstellt

**Prüfe:**
1. Ist `LEXWARE_API_KEY` gesetzt?
2. Sind die Logs aktiv? (`python manage.py runserver` zeigt Fehler)
3. Hat der Benutzer bereits einen Lexware-Kontakt?

```python
# Prüfen ob Kontakt existiert
user = User.objects.get(email='user@example.com')
print(f"Lexware Contact ID: {user.lexware_contact_id}")
print(f"Customer Number: {user.lexware_customer_number}")
```

## 📈 Monitoring

### Lexware-Status prüfen

Status-Seite: https://status.lexware.de/

### Statistiken abrufen

```python
from accounts.models import User

# Anzahl Benutzer mit Lexware-Kontakt
total_users = User.objects.count()
users_with_lexware = User.objects.filter(lexware_contact_id__isnull=False).count()

print(f"Gesamt: {total_users}")
print(f"Mit Lexware: {users_with_lexware}")
print(f"Ohne Lexware: {total_users - users_with_lexware}")
```

## 📝 Changelog

### Version 1.0.0 (2025-12-26)

- ✅ Initiale Implementation der Lexware-Integration
- ✅ Automatische Kundenerstellung bei Registrierung
- ✅ Management Command für bestehende Benutzer
- ✅ Unterstützung für Privat- und Firmenkunden
- ✅ Fehlertolerante Implementierung

## 🤝 Support

Bei Fragen oder Problemen:
- **Lexware API Dokumentation**: https://developers.lexware.io/docs/
- **Lexware Support**: https://office.lexware.de/kontakt/
- **Auth-Service Team**: Dein internes Team

## 📄 Lizenz

Diese Integration ist Teil des PalmDynamicX Auth-Service Projekts.
