# Test: Lexware Validierung

## Test 1: Unvollständiges Profil (wie im Beispiel)
```json
{
  "email": "palmservers@palmdynamicx.de",
  "username": "testuser",
  "password": "Test123!",
  "password2": "Test123!",
  "first_name": "Test",
  "last_name": "User",
  "website_id": "uuid"
  // Keine Adresse!
}
```

**Erwartetes Ergebnis:**
```json
{
  "user": { ... },
  "tokens": { ... },
  "message": "Benutzer erfolgreich registriert.",
  "verification_email_sent": true,
  "lexware_customer_number": null,  // ← Kein Lexware-Kontakt erstellt
  "lexware_warning": "Profil unvollständig für Lexware (fehlende Felder: Straße, Stadt, PLZ)"
}
```

## Test 2: Vollständiges Profil
```json
{
  "email": "complete@example.com",
  "username": "completeuser",
  "password": "Test123!",
  "password2": "Test123!",
  "first_name": "Max",
  "last_name": "Mustermann",
  "street": "Musterstraße",
  "street_number": "123",
  "city": "Berlin",
  "postal_code": "10115",
  "country": "Deutschland",
  "website_id": "uuid"
}
```

**Erwartetes Ergebnis:**
```json
{
  "user": { ... },
  "tokens": { ... },
  "message": "Benutzer erfolgreich registriert.",
  "verification_email_sent": true,
  "lexware_customer_number": 10020,  // ← Lexware-Kontakt erstellt!
  "lexware_contact_id": "uuid"
}
```

## Test 3: Management Command
```bash
python manage.py sync_lexware_contacts --create-missing

# Output:
✓ Kontakt erstellt für complete@example.com - Kundennummer: 10020
⊘ Übersprungen: palmservers@palmdynamicx.de - Fehlende Pflichtfelder: Straße, Stadt, PLZ
```

## Test 4: complete-profile
```bash
# Erst unvollständig registrieren
POST /api/accounts/register/
{
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
  # Keine Adresse
}

# Dann Profil vervollständigen
POST /api/accounts/complete-profile/
{
  "street": "Teststraße",
  "street_number": "42",
  "city": "München",
  "postal_code": "80331",
  "country": "Deutschland"
}

# Response:
{
  "user": { ... },
  "message": "Profil erfolgreich vervollständigt.",
  "lexware_created": true,  // ← Jetzt erstellt!
  "lexware_customer_number": 10021
}
```
