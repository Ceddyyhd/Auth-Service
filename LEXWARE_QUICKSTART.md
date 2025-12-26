# 🎯 Lexware Integration - Schnellstart

## Was wurde implementiert?

Die Lexware API Integration erstellt automatisch bei jeder Benutzerregistrierung einen Kundenkontakt in Lexware und speichert die Kundennummer im Auth-Service.

## ⚡ Quick Setup (3 Schritte)

### 1. Lexware API Key holen
```bash
# Gehe zu: https://app.lexware.de/addons/public-api
# Klicke auf "API-Schlüssel generieren"
# Kopiere den generierten Key
```

### 2. In .env eintragen
```env
LEXWARE_API_KEY=dein_api_key_hier
```

### 3. Migration ausführen
```bash
python manage.py migrate accounts
```

## ✅ Fertig!

Ab jetzt wird bei jeder Registrierung automatisch ein Lexware-Kontakt erstellt:

```python
# Neue Registrierung
POST /api/accounts/register/
{
  "email": "kunde@example.com",
  "username": "kunde123",
  "password": "SecurePass123!",
  "first_name": "Max",
  "last_name": "Mustermann",
  "city": "Berlin",
  "postal_code": "10115"
}

# Response
{
  "user": {
    "lexware_customer_number": 10001,  # ← Automatisch erstellt!
    "lexware_contact_id": "uuid-hier"
  },
  "tokens": {...}
}
```

## 🔄 Bestehende Benutzer synchronisieren

```bash
# Für alle Benutzer ohne Lexware-Kontakt
python manage.py sync_lexware_contacts --create-missing

# Test ohne Änderungen
python manage.py sync_lexware_contacts --create-missing --dry-run
```

## 📊 Status prüfen

```python
from accounts.models import User

# Wie viele haben Lexware-Kontakt?
User.objects.filter(lexware_contact_id__isnull=False).count()
```

## 📖 Vollständige Dokumentation

Siehe [LEXWARE_INTEGRATION.md](LEXWARE_INTEGRATION.md) für:
- Detaillierte API-Dokumentation
- Fehlerbehandlung
- Erweiterte Konfiguration
- Troubleshooting
- Code-Beispiele

## 🆘 Probleme?

**"API Key nicht konfiguriert"** → Prüfe `.env` Datei  
**"401 Unauthorized"** → API Key ist falsch/abgelaufen  
**"Kontakt wird nicht erstellt"** → Logs prüfen: `python manage.py runserver`

---

**Lexware Status**: https://status.lexware.de/  
**API Docs**: https://developers.lexware.io/docs/
