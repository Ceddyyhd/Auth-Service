# 🚀 Quick Start - Berechtigungen einrichten

## ⚡ In 5 Minuten: Benutzer mit Rechten erstellen

### Schritt 1: Berechtigung erstellen (30 Sek.)
```
Admin → Permissions System → Berechtigungen → Hinzufügen

📋 Name: Artikel erstellen
🔑 Codename: create_article
📝 Beschreibung: Erlaubt das Erstellen von Blog-Artikeln
🌍 Bereich: Lokal
🌐 Website: Meine Website

[Speichern]
```

### Schritt 2: Rolle erstellen (1 Min.)
```
Admin → Permissions System → Rollen → Hinzufügen

📋 Name: Blog Editor
📝 Beschreibung: Kann Artikel erstellen und bearbeiten
🌍 Bereich: Lokal
🌐 Website: Meine Website
🔑 Berechtigungen:
   ✅ Artikel erstellen
   ✅ Artikel bearbeiten
   ✅ Kommentare moderieren

[Speichern]
```

### Schritt 3: Benutzer mit Rolle (1 Min.)
```
Admin → Accounts → Benutzer → Benutzer bearbeiten

Scrolle nach unten zu:
"🎭 Rollen & Berechtigungen"

Klick auf grünes [+]
  Rolle: Blog Editor
  Website: Meine Website
  
[Speichern]
```

### ✅ Fertig!
Der Benutzer hat jetzt alle Berechtigungen der Rolle "Blog Editor" auf "Meine Website".

---

## 🎯 Häufige Szenarien

### 🌍 Global Admin (alle Websites)

**1. Berechtigungen erstellen:**
```
- "Benutzer verwalten" (global, codename: manage_users)
- "Systemlogs ansehen" (global, codename: view_system_logs)
- "Einstellungen ändern" (global, codename: change_settings)
```

**2. Rolle erstellen:**
```
Name: System Administrator
Bereich: Global
Website: — (leer)
Berechtigungen: Alle obigen ✅
```

**3. An Benutzer zuweisen:**
```
Benutzer → Rollen & Berechtigungen → [+]
  Rolle: System Administrator
  Website: — (leer lassen!)
```

---

### 🏠 Lokaler Editor (eine Website)

**1. Berechtigungen erstellen:**
```
- "Artikel erstellen" (lokal, Website: Blog A)
- "Artikel bearbeiten" (lokal, Website: Blog A)
- "Bilder hochladen" (lokal, Website: Blog A)
```

**2. Rolle erstellen:**
```
Name: Content Editor
Bereich: Lokal
Website: Blog A
Berechtigungen: Alle obigen ✅
```

**3. An Benutzer zuweisen:**
```
Benutzer → Rollen & Berechtigungen → [+]
  Rolle: Content Editor
  Website: Blog A
```

---

### 👥 Multi-Website Benutzer

**Ein Benutzer, mehrere Rollen:**
```
max@example.com

Zugewiesene Rollen:
  1) Support (Global, alle Websites)
     → Website: — (leer)
  
  2) Blog Editor (Lokal, Blog A)
     → Website: Blog A
  
  3) Shop Manager (Lokal, Shop B)
     → Website: Shop B
```

**Wie zuweisen:**
```
Benutzer max@example.com → Rollen & Berechtigungen

[+] Rolle: Support, Website: —
[+] Rolle: Blog Editor, Website: Blog A
[+] Rolle: Shop Manager, Website: Shop B

[Speichern]
```

---

### ⏰ Temporärer Zugriff

**Für Test-Accounts oder zeitlich begrenzten Zugang:**
```
Benutzer → Spezielle Berechtigungen → [+]

Berechtigung: Beta Features Zugang
Website: Meine Website
Gewährt: ✅ Ja
Läuft ab: 31.12.2025

[Speichern]
```

Nach Ablauf: Automatisch keine Berechtigung mehr!

---

## 🔍 Berechtigungen prüfen

### Im Admin:
```
Accounts → Benutzer
Spalte "Rollen" zeigt: ✅ 3 Rolle(n)

Klick auf Benutzer → Siehe alle Details
```

### Per API:
```bash
curl -X GET http://localhost:8000/api/permissions/users/USER_ID/permissions/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## 📊 Cheat Sheet

| Aktion | Ort im Admin |
|--------|--------------|
| Berechtigung erstellen | Permissions System → Berechtigungen |
| Rolle erstellen | Permissions System → Rollen |
| Rolle zuweisen | Accounts → Benutzer → [Benutzer] → Rollen Inline |
| Website erstellen | Accounts → Websites |
| Website Pflichtfelder | Accounts → Websites → [Website] |
| Social Login Setup | Siehe GOOGLE_SETUP.md |

---

## 🎓 Wichtige Konzepte

### Global vs. Lokal
```
🌍 GLOBAL = Alle Websites
  Beispiel: System Admin kann auf ALLEN Websites Benutzer verwalten

🏠 LOKAL = Eine Website
  Beispiel: Blog Editor kann nur auf "Blog A" Artikel erstellen
```

### Rollen vs. Direkte Berechtigungen
```
🎭 ROLLEN (empfohlen)
  ✅ Wiederverwendbar
  ✅ Einfach zu verwalten
  ✅ Mehrere Berechtigungen gebündelt

🔐 DIREKTE BERECHTIGUNGEN (Ausnahmen)
  ⚠️ Nur für Sonderfälle
  ⚠️ Temporäre Zugriffe
  ⚠️ Test-Accounts
```

### Mehrere Rollen
```
✅ EIN Benutzer kann MEHRERE Rollen haben!

Beispiel:
  max@example.com
    → Support (global)
    → Editor (lokal, Website A)
    → Manager (lokal, Website B)
```

---

## ❓ FAQ

**Q: Kann ein Benutzer mehrere Rollen haben?**  
A: ✅ Ja! Unbegrenzt viele Rollen möglich.

**Q: Was ist der Unterschied zwischen global und lokal?**  
A: Global = alle Websites, Lokal = eine spezifische Website.

**Q: Wie entferne ich eine Rolle?**  
A: Benutzer → Rollen & Berechtigungen → [X] Löschen

**Q: Kann ich zeitlich begrenzte Berechtigungen vergeben?**  
A: ✅ Ja, über "Spezielle Berechtigungen" mit Ablaufdatum.

**Q: Wo sind die Django Groups hin?**  
A: Absichtlich ausgeblendet! Nutze unser vereinfachtes System.

---

## 🆘 Hilfe

- **Vollständige Anleitung:** [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md)
- **Social Login Setup:** [SOCIAL_LOGIN.md](SOCIAL_LOGIN.md)
- **Google OAuth:** [GOOGLE_SETUP.md](GOOGLE_SETUP.md)
- **API Dokumentation:** http://localhost:8000/api/docs/

---

**Viel Erfolg! 🎉**
