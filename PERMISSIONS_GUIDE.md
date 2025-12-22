# 🎭 Berechtigungs-System - Vereinfachte Übersicht

## 📊 Konzept-Hierarchie

```
👤 BENUTZER
  └─ 🎭 ROLLEN (mehrere möglich)
      └─ 🔑 BERECHTIGUNGEN (viele pro Rolle)
  └─ 🔐 Spezielle Berechtigungen (optional, direkt)
```

## 🌍 Global vs. Lokal

### Global 🌍
- Gilt für **alle Websites**
- Unabhängig vom Website-Kontext
- Beispiele:
  - "System Administrator" (Rolle)
  - "Alle Logs einsehen" (Berechtigung)

### Lokal 🏠
- Gilt nur für **eine spezifische Website**
- Website-spezifisch
- Beispiele:
  - "Blog Editor von Website A" (Rolle)
  - "Artikel in Website B erstellen" (Berechtigung)

---

## 🔧 Verwaltung im Admin

### 1️⃣ **Berechtigungen definieren** (`Permissions`)

**Wo:** Admin → Permissions System → Berechtigungen

Eine Berechtigung ist die **kleinste Einheit** im System.

**Beispiele:**
```
📋 Name: Artikel erstellen
🔑 Codename: create_article
🌍 Bereich: Lokal
🌐 Website: Blog Website

📋 Name: Benutzer löschen
🔑 Codename: delete_user
🌍 Bereich: Global
🌐 Website: —
```

**Wichtig:**
- Global = Website-Feld leer lassen
- Lokal = Website auswählen

---

### 2️⃣ **Rollen erstellen** (`Roles`)

**Wo:** Admin → Permissions System → Rollen

Eine Rolle **bündelt mehrere Berechtigungen**.

**Beispiele:**

#### Globale Rolle: "Super Admin"
```
📋 Name: Super Admin
🌍 Bereich: Global
🌐 Website: —
🔑 Berechtigungen:
  ✅ Benutzer erstellen (global)
  ✅ Benutzer löschen (global)
  ✅ Alle Logs einsehen (global)
  ✅ Systemeinstellungen ändern (global)
```

#### Lokale Rolle: "Blog Editor"
```
📋 Name: Blog Editor
🌍 Bereich: Lokal
🌐 Website: Meine Blog Website
🔑 Berechtigungen:
  ✅ Artikel erstellen (lokal)
  ✅ Artikel bearbeiten (lokal)
  ✅ Kommentare moderieren (lokal)
```

---

### 3️⃣ **Rollen an Benutzer zuweisen**

**Wo:** Admin → Accounts → Benutzer → Benutzer bearbeiten

Im **Benutzerprofil** findest du unten:

#### 🎭 Rollen & Berechtigungen (Inline-Tabelle)

| Rolle | Website | Zugewiesen am |
|-------|---------|---------------|
| Super Admin (Global) | — | 22.12.2025 |
| Blog Editor (Lokal) | Meine Blog Website | 22.12.2025 |
| Shop Manager (Lokal) | Online Shop | 22.12.2025 |

**Klicke auf "+" um neue Rolle hinzuzufügen:**
1. Rolle auswählen (z.B. "Blog Editor")
2. Website auswählen (falls lokale Rolle)
3. Speichern

**Mehrere Rollen möglich!** ✅
- Ein Benutzer kann mehrere Rollen haben
- Globale + Lokale Rollen kombinierbar
- Beispiel: "Super Admin" (global) + "Blog Editor" (lokal auf Website A) + "Shop Manager" (lokal auf Website B)

---

#### 🔐 Spezielle Berechtigungen (optional)

Für **Sonderfälle** kannst du einzelne Berechtigungen direkt vergeben:

| Berechtigung | Website | Gewährt | Läuft ab |
|--------------|---------|---------|----------|
| VIP-Zugang | Website A | ✅ Ja | 31.12.2025 |
| Beta-Features | Website B | ✅ Ja | — |

**Wann verwenden?**
- ✅ Temporäre Berechtigungen (mit Ablaufdatum)
- ✅ Test-Zugriffe
- ✅ Spezielle Ausnahmen
- ❌ **Nicht** für normale Benutzer verwenden (nutze Rollen!)

**Negation möglich:**
- Gewährt = ❌ Nein → Explizite Verweigerung (überschreibt Rolle!)

---

## 📝 Schritt-für-Schritt: Neuen Benutzer mit Rechten erstellen

### Szenario: Editor für Blog Website

**Schritt 1: Berechtigung erstellen (falls noch nicht vorhanden)**
```
Admin → Permissions → Berechtigung hinzufügen
  Name: Artikel erstellen
  Codename: create_article
  Bereich: Lokal
  Website: Meine Blog Website
```

**Schritt 2: Rolle erstellen**
```
Admin → Rollen → Rolle hinzufügen
  Name: Blog Editor
  Bereich: Lokal
  Website: Meine Blog Website
  Berechtigungen: 
    ✅ Artikel erstellen
    ✅ Artikel bearbeiten
    ✅ Kommentare moderieren
```

**Schritt 3: Benutzer erstellen und Rolle zuweisen**
```
Admin → Benutzer → Benutzer hinzufügen
  Email: editor@example.com
  Username: editor
  Passwort: ********
  
  → Benutzer speichern
  
  → Scrollen zu "Rollen & Berechtigungen"
  → Klick auf grünes "+"
  → Rolle: Blog Editor
  → Website: Meine Blog Website
  → Speichern
```

**Fertig! ✅** Der Benutzer hat jetzt alle Berechtigungen der "Blog Editor" Rolle auf "Meine Blog Website".

---

## 🎯 Häufige Anwendungsfälle

### 1. System Administrator (alle Websites)
```
Rolle: Super Admin (Global)
Berechtigungen:
  - Benutzer verwalten (global)
  - Alle Logs einsehen (global)
  - Systemeinstellungen (global)
  
Zuweisung:
  User → Rolle: Super Admin
  Website: — (leer lassen)
```

### 2. Editor auf einer Website
```
Rolle: Content Editor (Lokal)
Website: Blog A
Berechtigungen:
  - Artikel erstellen (lokal, Blog A)
  - Artikel bearbeiten (lokal, Blog A)
  
Zuweisung:
  User → Rolle: Content Editor
  Website: Blog A
```

### 3. Multi-Website Manager
```
Benutzer kann mehrere Rollen haben:

User: max@example.com
  → Rolle: Blog Editor (Lokal, Website: Blog A)
  → Rolle: Shop Manager (Lokal, Website: Shop B)
  → Rolle: Support (Global)
  
Der Benutzer hat:
  ✅ Editor-Rechte auf Blog A
  ✅ Manager-Rechte auf Shop B
  ✅ Support-Rechte auf allen Websites
```

### 4. Temporärer VIP-Zugang
```
Verwende Spezielle Berechtigungen:

User → Spezielle Berechtigung hinzufügen
  Berechtigung: VIP Features
  Website: Premium Shop
  Gewährt: ✅ Ja
  Läuft ab: 31.12.2025
  
Nach Ablauf: Automatisch keine Berechtigung mehr!
```

---

## ⚠️ Was wurde vereinfacht?

### Vorher (verwirrend):
- ❌ Separate "Benutzerrolle" Admin-Seite
- ❌ Separate "Benutzerberechtigung" Admin-Seite
- ❌ Django Groups und User Permissions gemischt
- ❌ Verwirrende Trennung zwischen verschiedenen Admin-Bereichen

### Jetzt (einfach):
- ✅ **Alles im Benutzerprofil**: Rollen direkt dort zuweisen
- ✅ **Klare Hierarchie**: Benutzer → Rollen → Berechtigungen
- ✅ **Keine Django Groups mehr**: Nur noch unser System
- ✅ **Inline-Editing**: Rollen direkt beim Benutzer hinzufügen/entfernen
- ✅ **Übersichtliche Icons**: 🎭 Rollen, 🔑 Berechtigungen, 🌍 Global, 🏠 Lokal

---

## 🔍 Benutzer-Rechte prüfen

### Im Admin:
1. Gehe zu **Benutzer**
2. Spalte **"Rollen"** zeigt: ✅ X Rolle(n) oder ❌ Keine Rollen
3. Klicke auf Benutzer → Siehe alle Rollen & Berechtigungen

### Per API:
```http
GET /api/permissions/users/{user_id}/permissions/
Authorization: Bearer {token}
```

Response:
```json
{
  "user": "max@example.com",
  "roles": [
    {
      "role": "Blog Editor",
      "scope": "local",
      "website": "Blog A",
      "permissions": [
        "create_article",
        "edit_article"
      ]
    },
    {
      "role": "Support",
      "scope": "global",
      "permissions": [
        "view_tickets",
        "reply_tickets"
      ]
    }
  ],
  "direct_permissions": []
}
```

---

## 💡 Best Practices

### ✅ DO:
- **Verwende Rollen** für normale Benutzer
- **Erstelle Rollen** die wiederverwendbar sind
- **Trenne Global/Lokal** klar
- **Mehrere Rollen** pro Benutzer wenn nötig
- **Aussagekräftige Namen** für Berechtigungen (z.B. "create_article" statt "perm1")

### ❌ DON'T:
- **Keine direkten Berechtigungen** für normale Use Cases (nutze Rollen!)
- **Nicht is_superuser** vergeben (nur für echte System-Admins)
- **Keine Django Groups** mehr verwenden (veraltet)
- **Keine leeren Rollen** erstellen

---

## 🚀 Quick Start Checkliste

- [ ] Berechtigungen definieren (z.B. "create_article", "delete_user")
- [ ] Rollen erstellen (z.B. "Editor", "Admin")
- [ ] Berechtigungen zu Rollen hinzufügen
- [ ] Benutzer erstellen
- [ ] Rollen an Benutzer zuweisen (direkt im Benutzerprofil)
- [ ] Testen: Benutzer einloggen und Rechte prüfen

---

**Alles zentral im Benutzerprofil! 🎯**
