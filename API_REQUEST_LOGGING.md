# 📊 API Request Logging System

## Übersicht

Das API Request Logging System loggt automatisch **alle API-Requests** mit detaillierten Informationen:

- ✅ **Wer**: Benutzer (oder Anonymous)
- ✅ **Wann**: Zeitstempel
- ✅ **Was**: HTTP Methode + Endpoint
- ✅ **Von wo**: IP-Adresse, User-Agent, Referer
- ✅ **Request**: Body, Query Parameter, Headers
- ✅ **Response**: Body, Status Code
- ✅ **Performance**: Request-Dauer in Millisekunden

---

## 🔧 Implementierung

### 1. Middleware aktiviert
Die `APIRequestLoggingMiddleware` ist in `auth_service/settings.py` aktiviert und loggt automatisch alle Requests die mit `/api/` beginnen.

### 2. Model: APIRequestLog
Speichert alle Log-Einträge in der Datenbank:

```python
class APIRequestLog(models.Model):
    user           # Benutzer (oder null für Anonymous)
    method         # GET, POST, PUT, DELETE, etc.
    path           # /api/accounts/register/
    query_params   # ?page=1&limit=10
    request_body   # JSON Request Body (Passwörter maskiert)
    response_body  # JSON Response Body (Tokens maskiert)
    status_code    # 200, 404, 500, etc.
    ip_address     # Client IP (auch hinter Proxy)
    user_agent     # Browser/Client Info
    headers        # Wichtige HTTP Headers
    referer        # Von welcher Seite
    duration       # Request-Dauer in Sekunden
    timestamp      # Wann wurde angefragt
```

### 3. Sicherheit
**Sensible Daten werden automatisch maskiert**:
- ❌ Passwörter: `password`, `password2`, `old_password`, `new_password`
- ❌ Tokens: `access`, `refresh`, `token`, `access_token`, `refresh_token`
- ❌ Credentials: `api_key`, `api_secret`, `client_secret`

Alle diese Felder werden im Log als `***MASKED***` angezeigt.

---

## 📱 Admin Interface

### Zugriff
Django Admin → **API Request Logs**
URL: `https://auth.palmdynamicx.de/admin/accounts/apirequestlog/`

### Features

#### Liste-Ansicht
- ⏱️ **Zeitstempel**: Wann wurde angefragt
- 🔗 **Methode**: GET, POST, PUT, DELETE
- 📝 **Pfad**: Endpoint (gekürzt)
- 🎯 **Status Code**: 200, 404, 500, etc.
- 👤 **Benutzer**: E-Mail oder "Anonymous"
- 🌐 **IP-Adresse**: Client IP
- ⚡ **Dauer**: Response-Zeit in ms (farbcodiert)
- ✅/❌ **Status**: Erfolg/Fehler Indikator

#### Filter
- Nach **HTTP Methode** (GET, POST, etc.)
- Nach **Status Code** (200, 404, 500)
- Nach **Datum** (Heute, Letzte 7 Tage, etc.)
- Nach **Benutzer**

#### Suche
- Nach Pfad (`/api/accounts/login/`)
- Nach IP-Adresse (`192.168.1.1`)
- Nach Benutzer-E-Mail
- Nach Request/Response Body (Text-Suche)

#### Detail-Ansicht
Beim Klick auf einen Log-Eintrag:

**📊 Übersicht**
- ID, Zeitstempel, Dauer, Status Code

**🔗 Request**
- Methode, Pfad, Query Parameter
- Benutzer, IP-Adresse
- User-Agent, Referer

**📝 Request Details** (einklappbar)
- Formatiertes JSON (Pretty Print)
- Originaler Request Body

**📤 Response Details** (einklappbar)
- Formatiertes JSON (Pretty Print)
- Originaler Response Body

**🔧 Headers** (einklappbar)
- Formatierte HTTP Headers
- Content-Type, Accept, Origin, etc.

---

## 🎨 Visuelle Features

### Farbcodierung (Dauer)
- 🟢 **Grün**: < 100ms (schnell)
- 🟠 **Orange**: 100-500ms (mittel)
- 🔴 **Rot**: > 500ms (langsam)

### Status-Icons
- ✅ **Erfolg**: Status 200-299
- ⚠️ **Redirect**: Status 300-399
- ❌ **Fehler**: Status 400-599

---

## 📊 Verwendung

### Analyse-Beispiele

#### 1. Fehlerhafte Requests finden
```
Filter: Status Code = 500
→ Zeigt alle Server-Fehler
```

#### 2. Langsame Endpoints identifizieren
```
Sortieren nach: Dauer (absteigend)
→ Zeigt langsamste Requests zuerst
```

#### 3. Verdächtige Aktivität prüfen
```
Suche: IP-Adresse = "1.2.3.4"
→ Zeigt alle Requests von dieser IP
```

#### 4. Benutzer-Aktivität verfolgen
```
Filter: Benutzer = user@example.com
→ Zeigt alle Requests dieses Benutzers
```

#### 5. API-Usage analysieren
```
Suche: /api/accounts/login/
→ Zeigt alle Login-Versuche
```

---

## ⚙️ Konfiguration

### Middleware-Reihenfolge
Die `APIRequestLoggingMiddleware` sollte **als letztes** in der MIDDLEWARE-Liste stehen (wie aktuell implementiert), damit sie:
- Zugriff auf authentifizierte Benutzer hat
- Die finale Response loggen kann
- Alle anderen Middleware bereits ausgeführt wurden

### Performance
- Logs werden **asynchron** erstellt (blockiert Request nicht)
- Bei Logging-Fehlern wird der Request **nicht** abgebrochen
- Request/Response Bodies werden auf **10.000 Zeichen** begrenzt
- IP-Adresse, User-Agent, Referer werden auf **500 Zeichen** begrenzt

### Speicherplatz
Logs akkumulieren sich über Zeit. Empfohlene Wartung:

**Option 1: Automatische Bereinigung (empfohlen)**
```python
# In Django Management Command
from datetime import timedelta
from django.utils import timezone
from accounts.models import APIRequestLog

# Logs älter als 30 Tage löschen
cutoff = timezone.now() - timedelta(days=30)
APIRequestLog.objects.filter(timestamp__lt=cutoff).delete()
```

**Option 2: Manuell im Admin**
Alte Logs manuell löschen über Django Admin

**Option 3: Database Rotation**
Separate Tabelle pro Monat (erfordert erweiterte Implementierung)

---

## 🔍 Debugging

### Request wurde nicht geloggt?
Prüfe:
1. Beginnt URL mit `/api/`? (Nur API-Requests werden geloggt)
2. Middleware aktiviert in `settings.py`?
3. Migration ausgeführt? (`python manage.py migrate accounts`)
4. Keine Datenbankfehler in Console?

### Sensible Daten im Log?
Die Middleware maskiert automatisch:
- Alle Felder mit "password" im Namen
- Alle Token-Felder (access, refresh, token)
- API Keys und Secrets

Falls neue sensible Felder hinzugefügt wurden, in `middleware.py` → `mask_sensitive_data()` → `sensitive_fields` ergänzen.

### Log-Eintrag ist zu groß?
- Request/Response Bodies werden automatisch auf 10.000 Zeichen begrenzt
- Text wird mit `... (truncated)` gekennzeichnet
- Binäre Daten werden als `[Binary or unreadable data]` angezeigt

---

## 📈 Zukünftige Erweiterungen

### Geplante Features
1. **Grafische Statistiken**
   - Request-Anzahl pro Stunde/Tag
   - Durchschnittliche Response-Zeiten
   - Error-Rate Dashboard

2. **Export-Funktionen**
   - CSV Export für Analyse
   - JSON Export für externe Tools
   - Automatische Reports per E-Mail

3. **Erweiterte Filter**
   - Nach Dauer filtern (z.B. > 1 Sekunde)
   - Nach Response-Size
   - Kombinierte Filter

4. **Alerts**
   - E-Mail bei zu vielen Fehlern
   - Benachrichtigung bei langsamen Endpoints
   - Verdächtige Aktivität melden

5. **Archivierung**
   - Automatische Archivierung alter Logs
   - Komprimierte Speicherung
   - Separate Datenbank für Logs

---

## 🚀 Quick Start

### 1. Migration ausführen
```bash
python manage.py migrate accounts
```

### 2. API Request testen
```bash
curl -X POST https://auth.palmdynamicx.de/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### 3. Log prüfen
```
Django Admin → API Request Logs
→ Neuer Eintrag sollte erscheinen
```

---

## 📝 Beispiel Log-Eintrag

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": "user@example.com",
  "method": "POST",
  "path": "/api/accounts/login/",
  "query_params": null,
  "request_body": {
    "username": "user@example.com",
    "password": "***MASKED***"
  },
  "response_body": {
    "access": "***MASKED***",
    "refresh": "***MASKED***",
    "user": {
      "id": "...",
      "email": "user@example.com"
    }
  },
  "status_code": 200,
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "headers": {
    "content-type": "application/json",
    "accept": "application/json",
    "origin": "https://example.com"
  },
  "referer": "https://example.com/login",
  "duration": 0.234,
  "timestamp": "2025-12-27T10:30:00Z"
}
```

---

**Status**: ✅ Vollständig implementiert und einsatzbereit
