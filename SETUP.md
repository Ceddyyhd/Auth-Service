# Setup-Anleitung für Auth Service

## Schritt 1: Virtuelle Umgebung & Dependencies

```powershell
# In PowerShell (als Administrator wenn nötig)
cd "c:\Users\Cedric\Desktop\PalmDynamicX\Auth-Service"

# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren
.\venv\Scripts\Activate.ps1

# Falls Fehler: Execution Policy anpassen
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Dependencies installieren
pip install -r requirements.txt
```

## Schritt 2: Datenbank konfigurieren

### Option A: SQLite (Einfach für Entwicklung)
Keine zusätzliche Konfiguration nötig! Django verwendet automatisch SQLite.

### Option B: PostgreSQL (Empfohlen für Produktion)

1. PostgreSQL installieren: https://www.postgresql.org/download/windows/

2. Datenbank erstellen:
```sql
CREATE DATABASE auth_service;
CREATE USER auth_admin WITH PASSWORD 'ihr-passwort';
GRANT ALL PRIVILEGES ON DATABASE auth_service TO auth_admin;
```

3. `.env` Datei erstellen:
```powershell
copy .env.example .env
```

4. `.env` bearbeiten und PostgreSQL-Zugangsdaten eintragen

## Schritt 3: Redis installieren (Optional)

### Windows:
1. Download: https://github.com/microsoftarchive/redis/releases
2. Installieren und als Service starten

### Alternative: Memurai (Redis für Windows)
https://www.memurai.com/

### Redis nicht verfügbar?
Kommentieren Sie in `settings.py` die Redis-Cache-Konfiguration aus.

## Schritt 4: Datenbank migrieren

```powershell
python manage.py makemigrations
python manage.py migrate
```

## Schritt 5: Superuser erstellen

```powershell
python manage.py createsuperuser
```

Eingeben:
- Email: admin@example.com
- Username: admin
- Password: (Ihr sicheres Passwort)

## Schritt 6: Server starten

```powershell
python manage.py runserver
```

Server läuft auf: http://localhost:8000

## Schritt 7: Admin-Interface testen

1. Öffnen Sie: http://localhost:8000/admin/
2. Login mit Ihren Superuser-Zugangsdaten
3. Erstellen Sie eine Test-Website:
   - Name: "Meine Website"
   - Domain: "localhost:3000"
   - Callback URL: "http://localhost:3000/auth/callback"

## Schritt 8: API-Dokumentation ansehen

Öffnen Sie: http://localhost:8000/api/docs/

## Schritt 9: Client Demo testen

Öffnen Sie: `client-demo.html` im Browser

## Häufige Probleme & Lösungen

### Problem: "Execution of scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: psycopg2 Installation schlägt fehl
```powershell
pip install psycopg2-binary
```

### Problem: Port 8000 bereits belegt
```powershell
python manage.py runserver 8001
```

### Problem: CORS-Fehler
Fügen Sie Ihre Frontend-URL zu `CORS_ALLOWED_ORIGINS` in `.env` hinzu:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500
```

## Produktions-Deployment

### Mit Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn auth_service.wsgi:application --bind 0.0.0.0:8000
```

### Mit Waitress (Windows)
```powershell
pip install waitress
waitress-serve --listen=*:8000 auth_service.wsgi:application
```

### Wichtige Produktions-Einstellungen

In `settings.py` oder `.env`:
```python
DEBUG=False
ALLOWED_HOSTS=ihre-domain.com,www.ihre-domain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## Nächste Schritte

1. ✅ Erstellen Sie Websites im Admin-Interface
2. ✅ Definieren Sie Permissions und Roles
3. ✅ Testen Sie die API mit Postman oder der Demo-Seite
4. ✅ Integrieren Sie den Client in Ihre Websites
5. ✅ Konfigurieren Sie Production-Settings

## Support

Bei Fragen oder Problemen:
1. Prüfen Sie die API-Dokumentation
2. Schauen Sie in die Logs: `python manage.py runserver --verbosity 2`
3. Testen Sie mit der Client-Demo-Seite

---

**Viel Erfolg mit Ihrem Auth Service! 🚀**
