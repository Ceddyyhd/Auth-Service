# 🎭 Berechtigungs-System - Vollständiger Leitfaden

## 🎯 Wichtig: Zentrale Verwaltung im Auth-Service

**⚠️ KERNKONZEPT: Alle Berechtigungen werden zentral im Auth-Service erstellt und verwaltet, dann auf den Client-Websites verwendet!**

```
┌─────────────────────────────────────────────────────────────┐
│  🔐 AUTH-SERVICE (auth.palmdynamicx.de)                     │
│  ═══════════════════════════════════════════════════════════│
│  • Berechtigungen ERSTELLEN                                 │
│  • Rollen DEFINIEREN                                        │
│  • Benutzer ZUWEISEN                                        │
│  • Zentrale VERWALTUNG                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JWT Token mit Berechtigungen
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 🌐 Website A│  │ 🌐 Website B│  │ 🌐 Website C│
│             │  │             │  │             │
│ PRÜFT       │  │ PRÜFT       │  │ PRÜFT       │
│ Rechte      │  │ Rechte      │  │ Rechte      │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 📊 Konzept-Hierarchie

```
👤 BENUTZER (im Auth-Service)
  └─ 🎭 ROLLEN (mehrere möglich)
      └─ 🔑 BERECHTIGUNGEN (viele pro Rolle)
  └─ 🔐 Spezielle Berechtigungen (optional, direkt)

📤 Benutzer loggt sich ein
  → JWT Token enthält alle Berechtigungen
    → Client-Website prüft Berechtigungen
      → Zugriff gewährt/verweigert
```

---

## 🌍 Global vs. Lokal (Website-spezifisch)

### Global 🌍
- Gilt für **alle Websites** im System
- Unabhängig vom Website-Kontext
- **Erstellt im**: Auth-Service Admin
- **Verwendet auf**: Alle verbundenen Websites
- **Beispiele**:
  - "System Administrator" (Rolle)
  - "Alle Logs einsehen" (Berechtigung)
  - "Benutzer verwalten" (Berechtigung)

### Lokal 🏠
- Gilt nur für **eine spezifische Website**
- Website-spezifisch
- **Erstellt im**: Auth-Service Admin (mit Website-Verknüpfung)
- **Verwendet auf**: Nur die zugewiesene Website
- **Beispiele**:
  - "Blog Editor von Website A" (Rolle)
  - "Artikel in Website B erstellen" (Berechtigung)
  - "Shop Manager von Website C" (Rolle)

---

## 🔧 Teil 1: Berechtigungen im Auth-Service erstellen

### ⚠️ Alle Schritte erfolgen im Auth-Service Admin-Panel!

**URL**: `https://auth.palmdynamicx.de/admin/`

---

### 1️⃣ **Berechtigungen definieren** (`Permissions`)

**Wo im Auth-Service**: Admin → Permissions System → Berechtigungen

Eine Berechtigung ist die **kleinste Einheit** im System.

#### Beispiel 1: Globale Berechtigung
```
📋 Name: Benutzer löschen
🔑 Codename: delete_user
📝 Beschreibung: Erlaubt das Löschen von Benutzern systemweit
🌍 Bereich: Global
🌐 Website: — (leer lassen!)
```

**Bedeutung**: Diese Berechtigung gilt auf ALLEN Websites!

#### Beispiel 2: Lokale Berechtigung
```
📋 Name: Artikel erstellen
🔑 Codename: create_article
📝 Beschreibung: Erlaubt das Erstellen von Blog-Artikeln
🌍 Bereich: Lokal
🌐 Website: Blog Website (auswählen!)
```

**Bedeutung**: Diese Berechtigung gilt NUR auf "Blog Website"!

#### Wichtige Codename-Konventionen:
- ✅ Verwende Verben: `create_`, `edit_`, `delete_`, `view_`
- ✅ Lowercase und Unterstriche: `create_article`, `manage_shop`
- ✅ Aussagekräftig: `delete_user` statt `perm1`
- ❌ Keine Leerzeichen oder Sonderzeichen

---

### 2️⃣ **Rollen erstellen** (`Roles`)

**Wo im Auth-Service**: Admin → Permissions System → Rollen

Eine Rolle **bündelt mehrere Berechtigungen**.

#### Beispiel 1: Globale Rolle
```
📋 Name: System Administrator
📝 Beschreibung: Vollzugriff auf alle Systeme
🌍 Bereich: Global
🌐 Website: — (leer lassen!)
🔑 Berechtigungen auswählen:
  ✅ Benutzer erstellen (global)
  ✅ Benutzer löschen (global)
  ✅ Benutzer bearbeiten (global)
  ✅ Alle Logs einsehen (global)
  ✅ Systemeinstellungen ändern (global)
```

**Verwendung**: Benutzer mit dieser Rolle haben die Rechte auf ALLEN Websites!

#### Beispiel 2: Lokale Rolle
```
📋 Name: Blog Editor
📝 Beschreibung: Kann Blog-Artikel verwalten
🌍 Bereich: Lokal
🌐 Website: Blog Website (auswählen!)
🔑 Berechtigungen auswählen:
  ✅ Artikel erstellen (lokal, Blog Website)
  ✅ Artikel bearbeiten (lokal, Blog Website)
  ✅ Artikel löschen (lokal, Blog Website)
  ✅ Kommentare moderieren (lokal, Blog Website)
```

**Verwendung**: Benutzer mit dieser Rolle haben die Rechte NUR auf "Blog Website"!

#### Beispiel 3: Weitere lokale Rolle
```
📋 Name: Shop Manager
📝 Beschreibung: Verwaltet Online-Shop
🌍 Bereich: Lokal
🌐 Website: Online Shop (auswählen!)
🔑 Berechtigungen:
  ✅ Produkte erstellen (lokal, Online Shop)
  ✅ Produkte bearbeiten (lokal, Online Shop)
  ✅ Bestellungen einsehen (lokal, Online Shop)
  ✅ Preise ändern (lokal, Online Shop)
```

---

### 3️⃣ **Rollen an Benutzer zuweisen**

**Wo im Auth-Service**: Admin → Accounts → Benutzer → [Benutzer bearbeiten]

Im **Benutzerprofil** nach unten scrollen zu:

#### 🎭 Rollen & Berechtigungen (Inline-Tabelle)

**Beispiel-Zuweisung:**

| Rolle | Website | Zugewiesen am | Aktion |
|-------|---------|---------------|--------|
| System Administrator (Global) | — | 22.12.2025 | 🗑️ |
| Blog Editor (Lokal) | Blog Website | 22.12.2025 | 🗑️ |
| Shop Manager (Lokal) | Online Shop | 23.12.2025 | 🗑️ |

**Neue Rolle hinzufügen:**
1. Klicke auf grünes **"+" Symbol**
2. Wähle **Rolle** aus Dropdown (z.B. "Blog Editor")
3. Wähle **Website** (nur bei lokalen Rollen sichtbar)
4. Klicke **Speichern**

**Mehrere Rollen möglich!** ✅
- Ein Benutzer kann beliebig viele Rollen haben
- Globale + Lokale Rollen kombinierbar
- Beispiel: "System Admin" (global) + "Blog Editor" (lokal auf Website A) + "Shop Manager" (lokal auf Website B)

---

#### 🔐 Spezielle Berechtigungen (optional)

Für **Sonderfälle** kannst du einzelne Berechtigungen direkt vergeben:

**Beispiel-Zuweisung:**

| Berechtigung | Website | Gewährt | Läuft ab | Aktion |
|--------------|---------|---------|----------|--------|
| VIP-Zugang | Website A | ✅ Ja | 31.12.2025 | 🗑️ |
| Beta-Features | Website B | ✅ Ja | — | 🗑️ |
| Artikel löschen | Blog | ❌ Nein | — | 🗑️ |

**Wann verwenden?**
- ✅ **Temporäre Berechtigungen** mit Ablaufdatum
- ✅ **Test-Zugriffe** für Beta-Features
- ✅ **Spezielle Ausnahmen** für einzelne Benutzer
- ✅ **Explizite Verweigerung** (Gewährt = Nein) überschreibt Rollen!
- ❌ **Nicht** für normale Benutzer verwenden (nutze Rollen!)

**Negation möglich:**
- Gewährt = ✅ Ja → Erlaubt die Berechtigung
- Gewährt = ❌ Nein → Explizite Verweigerung (überschreibt Rolle!)

---

## 📤 Teil 2: Berechtigungen auf Client-Websites verwenden

### Wie kommen die Berechtigungen zur Website?

#### 1. Benutzer meldet sich an
```javascript
// Website sendet Login an Auth-Service
const response = await fetch('https://auth.palmdynamicx.de/api/accounts/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
// data.access = JWT Token
// data.refresh = Refresh Token
```

#### 2. JWT Token für Authentifizierung
Der JWT Token vom Auth-Service wird für die Authentifizierung verwendet.

**Token-Inhalt (decodiert):**
```json
{
  "token_type": "access",
  "exp": 1767476645,
  "iat": 1767473045,
  "jti": "1f03e042114249a4a2c3dd2d42e3a2c3",
  "user_id": "165cba21-eac2-4a13-ae60-5f47fa5d816f"
}
```

**Wichtig**: ⚠️ Der Token enthält **KEINE** Berechtigungen! Diese müssen über die API abgerufen werden.

#### 3. Website prüft Berechtigungen via API

##### Beispiel A: Backend-Prüfung (Python/Django)
```python
# views.py auf der Client-Website
from django.http import JsonResponse
import jwt
import requests

def create_article(request):
    # 1. Token aus Header holen
    token = request.headers.get('Authorization').replace('Bearer ', '')
    
    # 2. Token decodieren um user_id zu erhalten
    decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    user_id = decoded.get('user_id')
    
    # 3. Berechtigungen vom Auth-Service abfragen
    response = requests.post(
        'https://auth.palmdynamicx.de/api/permissions/check/',
        headers={
            'Authorization': f'Bearer {token}',
            'X-API-Key': settings.AUTH_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'permission': 'create_article',
            'website_id': settings.WEBSITE_ID
        }
    )
    
    data = response.json()
    
    if not data.get('has_permission'):
        return JsonResponse({'error': 'Keine Berechtigung'}, status=403)
    
    # 4. Berechtigung vorhanden - Artikel erstellen
    # ... Code zum Erstellen des Artikels ...
    
    return JsonResponse({'message': 'Artikel erstellt'})
```

##### Beispiel B: Backend-Prüfung (Node.js/Express)
```javascript
// routes/articles.js auf der Client-Website
const jwt = require('jsonwebtoken');
const axios = require('axios');

app.post('/api/articles', async (req, res) => {
  // 1. Token aus Header holen
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  // 2. Token decodieren um user_id zu erhalten
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  
  // 3. Berechtigungen vom Auth-Service abfragen
  try {
    const response = await axios.post(
      'https://auth.palmdynamicx.de/api/permissions/check/',
      {
        permission: 'create_article',
        website_id: process.env.WEBSITE_ID
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-API-Key': process.env.AUTH_API_KEY,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.data.has_permission) {
      return res.status(403).json({ error: 'Keine Berechtigung' });
    }
    
    // 4. Berechtigung vorhanden - Artikel erstellen
    // ... Code zum Erstellen des Artikels ...
    
    res.json({ message: 'Artikel erstellt' });
  } catch (error) {
    res.status(500).json({ error: 'Fehler bei Berechtigungsprüfung' });
  }
});
```

##### Beispiel C: Frontend-Prüfung (React/Vue)
```javascript
// CheckPermission.jsx - React Component
import { useState, useEffect } from 'react';

function CheckPermission({ permission, websiteId, children }) {
  const [hasPermission, setHasPermission] = useState(false);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkPermission = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await fetch(
          'https://auth.palmdynamicx.de/api/permissions/check/',
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'X-API-Key': process.env.REACT_APP_AUTH_API_KEY,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              permission: permission,
              website_id: websiteId
            })
          }
        );
        
        const data = await response.json();
        setHasPermission(data.has_permission || false);
      } catch (error) {
        console.error('Fehler bei Berechtigungsprüfung:', error);
        setHasPermission(false);
      } finally {
        setLoading(false);
      }
    };
    
    checkPermission();
  }, [permission, websiteId]);
  
  if (loading) return null;
  
  return hasPermission ? children : null;
}

// Verwendung:
<CheckPermission permission="create_article" websiteId="blog-website-uuid">
  <button onClick={createArticle}>Artikel erstellen</button>
</CheckPermission>

// Button wird nur angezeigt, wenn Berechtigung vorhanden!
```

##### Beispiel D: Berechtigungen cachen für bessere Performance
```javascript
// Cache für Berechtigungen mit TTL
class PermissionCache {
  constructor(ttl = 5 * 60 * 1000) { // 5 Minuten
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  async checkPermission(permission, websiteId, token, apiKey) {
    const cacheKey = `${permission}:${websiteId}`;
    const cached = this.cache.get(cacheKey);
    
    // Prüfe ob Cache noch gültig
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.hasPermission;
    }
    
    // Cache abgelaufen oder nicht vorhanden - API-Call
    const response = await fetch(
      'https://auth.palmdynamicx.de/api/permissions/check/',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-API-Key': apiKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          permission: permission,
          website_id: websiteId
        })
      }
    );
    
    const data = await response.json();
    const hasPermission = data.has_permission || false;
    
    // In Cache speichern
    this.cache.set(cacheKey, {
      hasPermission,
      timestamp: Date.now()
    });
    
    return hasPermission;
  }
  
  clearCache() {
    this.cache.clear();
  }
}

// Verwendung:
const permissionCache = new PermissionCache();

const hasPermission = await permissionCache.checkPermission(
  'create_article',
  'blog-website-uuid',
  accessToken,
  'YOUR_API_KEY'
);
```

---

## 📝 Komplettes Beispiel: Blog-Website mit Berechtigungen

### Schritt 1: Im Auth-Service - Berechtigungen erstellen

**URL**: `https://auth.palmdynamicx.de/admin/`

#### 1.1 Berechtigungen definieren
```
Admin → Permissions → Berechtigung hinzufügen

Berechtigung 1:
  Name: Artikel erstellen
  Codename: create_article
  Beschreibung: Erlaubt das Erstellen von Blog-Artikeln
  Bereich: Lokal
  Website: Blog Website ← Auswählen!

Berechtigung 2:
  Name: Artikel bearbeiten
  Codename: edit_article
  Beschreibung: Erlaubt das Bearbeiten von Blog-Artikeln
  Bereich: Lokal
  Website: Blog Website

Berechtigung 3:
  Name: Artikel löschen
  Codename: delete_article
  Beschreibung: Erlaubt das Löschen von Blog-Artikeln
  Bereich: Lokal
  Website: Blog Website

Berechtigung 4:
  Name: Artikel veröffentlichen
  Codename: publish_article
  Beschreibung: Erlaubt das Veröffentlichen von Artikeln
  Bereich: Lokal
  Website: Blog Website
```

#### 1.2 Rollen erstellen
```
Admin → Roles → Rolle hinzufügen

Rolle 1: Blog Autor
  Name: Blog Autor
  Beschreibung: Kann Artikel erstellen und bearbeiten
  Bereich: Lokal
  Website: Blog Website
  Berechtigungen:
    ✅ Artikel erstellen (create_article)
    ✅ Artikel bearbeiten (edit_article)

Rolle 2: Blog Editor
  Name: Blog Editor
  Beschreibung: Kann Artikel verwalten und veröffentlichen
  Bereich: Lokal
  Website: Blog Website
  Berechtigungen:
    ✅ Artikel erstellen (create_article)
    ✅ Artikel bearbeiten (edit_article)
    ✅ Artikel löschen (delete_article)
    ✅ Artikel veröffentlichen (publish_article)
```

#### 1.3 Benutzer erstellen und Rollen zuweisen
```
Admin → Accounts → Benutzer → Benutzer hinzufügen

Benutzer 1:
  Email: autor@blog.com
  Username: blog_autor
  Passwort: ********
  
  → Speichern
  → Scrollen zu "Rollen & Berechtigungen"
  → Klick auf grünes "+"
  → Rolle: Blog Autor
  → Website: Blog Website
  → Speichern

Benutzer 2:
  Email: editor@blog.com
  Username: blog_editor
  Passwort: ********
  
  → Speichern
  → Scrollen zu "Rollen & Berechtigungen"
  → Klick auf grünes "+"
  → Rolle: Blog Editor
  → Website: Blog Website
  → Speichern
```

**Fertig im Auth-Service! ✅**

---

### Schritt 2: Auf der Blog-Website - Berechtigungen prüfen

**Die Blog-Website läuft auf**: `https://blog.example.com`

#### 2.1 Backend - API-Route schützen (Node.js)

```javascript
// routes/articles.js auf blog.example.com
const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');

// Middleware: Berechtigung prüfen
function requirePermission(permission) {
  return (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Nicht angemeldet' });
    }
    
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const websiteId = process.env.WEBSITE_ID; // "blog-website-uuid"
      
      // Prüfe lokale Berechtigungen
      const permissions = decoded.permissions?.local?.[websiteId] || [];
      
      // Prüfe globale Berechtigungen
      const globalPermissions = decoded.permissions?.global || [];
      
      // Berechtigung vorhanden?
      if (permissions.includes(permission) || globalPermissions.includes(permission)) {
        req.user = decoded;
        next();
      } else {
        res.status(403).json({ 
          error: 'Keine Berechtigung',
          required: permission 
        });
      }
    } catch (error) {
      res.status(401).json({ error: 'Ungültiger Token' });
    }
  };
}

// Route: Artikel erstellen (benötigt "create_article")
router.post('/articles', requirePermission('create_article'), async (req, res) => {
  // Nur Benutzer mit "create_article" Berechtigung kommen hier an!
  const article = await createArticle(req.body);
  res.json(article);
});

// Route: Artikel bearbeiten (benötigt "edit_article")
router.put('/articles/:id', requirePermission('edit_article'), async (req, res) => {
  const article = await updateArticle(req.params.id, req.body);
  res.json(article);
});

// Route: Artikel löschen (benötigt "delete_article")
router.delete('/articles/:id', requirePermission('delete_article'), async (req, res) => {
  await deleteArticle(req.params.id);
  res.json({ message: 'Artikel gelöscht' });
});

// Route: Artikel veröffentlichen (benötigt "publish_article")
router.post('/articles/:id/publish', requirePermission('publish_article'), async (req, res) => {
  const article = await publishArticle(req.params.id);
  res.json(article);
});

module.exports = router;
```

#### 2.2 Frontend - UI-Elemente bedingt anzeigen (React)

```javascript
// components/ArticleActions.jsx auf blog.example.com
import React from 'react';
import { jwtDecode } from 'jwt-decode';

// Hook: Berechtigungen abrufen
function usePermissions() {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchPermissions = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        // Hole user_id aus Token
        const decoded = jwtDecode(token);
        const userId = decoded.user_id;
        
        // Hole alle Berechtigungen vom Auth-Service
        const response = await fetch(
          `https://auth.palmdynamicx.de/api/permissions/users/${userId}/permissions/`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'X-API-Key': process.env.REACT_APP_AUTH_API_KEY
            }
          }
        );
        
        const data = await response.json();
        const websiteId = process.env.REACT_APP_WEBSITE_ID;
        
        // Extrahiere Berechtigungen für diese Website
        let allPerms = [];
        
        data.roles?.forEach(role => {
          if (role.scope === 'global' || role.website?.id === websiteId) {
            allPerms = [...allPerms, ...role.permissions];
          }
        });
        
        setPermissions([...new Set(allPerms)]); // Duplikate entfernen
      } catch (error) {
        console.error('Fehler beim Laden der Berechtigungen:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPermissions();
  }, []);
  
  return {
    permissions,
    loading,
    hasPermission: (perm) => permissions.includes(perm)
  };
}

// Component: Artikel-Aktionen
function ArticleActions({ articleId }) {
  const { hasPermission, loading } = usePermissions();
  
  if (loading) return <div>Lädt...</div>;
  
  return (
    <div className="article-actions">
      {/* Bearbeiten-Button: Nur mit "edit_article" */}
      {hasPermission('edit_article') && (
        <button onClick={() => editArticle(articleId)}>
          ✏️ Bearbeiten
        </button>
      )}
      
      {/* Löschen-Button: Nur mit "delete_article" */}
      {hasPermission('delete_article') && (
        <button onClick={() => deleteArticle(articleId)}>
          🗑️ Löschen
        </button>
      )}
      
      {/* Veröffentlichen-Button: Nur mit "publish_article" */}
      {hasPermission('publish_article') && (
        <button onClick={() => publishArticle(articleId)}>
          🚀 Veröffentlichen
        </button>
      )}
    </div>
  );
}

// Component: Erstellen-Button in der Übersicht
function ArticleList() {
  const { hasPermission } = usePermissions();
  
  return (
    <div>
      <h1>Blog-Artikel</h1>
      
      {/* Erstellen-Button: Nur mit "create_article" */}
      {hasPermission('create_article') && (
        <button onClick={() => window.location.href = '/articles/new'}>
          ➕ Neuer Artikel
        </button>
      )}
      
      {/* Artikel-Liste */}
      {/* ... */}
    </div>
  );
}

export { ArticleActions, ArticleList };
```

#### 2.3 Was passiert im Beispiel?

**Benutzer: `autor@blog.com` (Rolle: Blog Autor)**
```
Berechtigungen:
  ✅ create_article
  ✅ edit_article
  ❌ delete_article
  ❌ publish_article

Kann:
  ✅ Artikel erstellen
  ✅ Artikel bearbeiten
  ❌ Artikel löschen (Button wird nicht angezeigt)
  ❌ Artikel veröffentlichen (Button wird nicht angezeigt)
```

**Benutzer: `editor@blog.com` (Rolle: Blog Editor)**
```
Berechtigungen:
  ✅ create_article
  ✅ edit_article
  ✅ delete_article
  ✅ publish_article

Kann:
  ✅ Artikel erstellen
  ✅ Artikel bearbeiten
  ✅ Artikel löschen
  ✅ Artikel veröffentlichen
```

---

## 🎯 Häufige Anwendungsfälle mit Implementierung

### Anwendungsfall 1: Multi-Website Manager

**Szenario**: Ein Benutzer verwaltet mehrere Websites

#### Im Auth-Service erstellen:
```
Benutzer: max@example.com

Rollen zuweisen:
  → Rolle: Blog Editor
     Website: Blog A
  → Rolle: Shop Manager
     Website: Online Shop
  → Rolle: Support
     Website: — (global)
```

#### Auf den Websites verwenden:
```javascript
// Berechtigungen vom Auth-Service abrufen
async function getUserPermissions(userId, token, apiKey) {
  const response = await fetch(
    `https://auth.palmdynamicx.de/api/permissions/users/${userId}/permissions/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-API-Key': apiKey
      }
    }
  );
  
  const data = await response.json();
  return data;
}

// Auf Blog A (blog-a.com)
const permissions = await getUserPermissions(userId, token, apiKey);
const blogARole = permissions.roles.find(r => r.website?.id === 'blog-a-uuid');
const blogAPermissions = blogARole?.permissions || [];
// ['create_article', 'edit_article', 'delete_article']

// Auf Online Shop (shop.com)
const shopRole = permissions.roles.find(r => r.website?.id === 'shop-uuid');
const shopPermissions = shopRole?.permissions || [];
// ['create_product', 'edit_product', 'view_orders']

// Global (auf allen Websites)
const globalRoles = permissions.roles.filter(r => r.scope === 'global');
const globalPermissions = globalRoles.flatMap(r => r.permissions);
// ['view_tickets', 'reply_tickets']
```

---

### Anwendungsfall 2: Temporärer VIP-Zugang

**Szenario**: Einem Benutzer für 1 Monat VIP-Features gewähren

#### Im Auth-Service:
```
Benutzer bearbeiten → Spezielle Berechtigungen

→ Berechtigung hinzufügen:
  Berechtigung: VIP Features (vip_access)
  Website: Premium Website
  Gewährt: ✅ Ja
  Läuft ab: 31.01.2026
```

#### Auf der Website prüfen:
```javascript
async function hasVIPAccess(userId, websiteId, token, apiKey) {
  // Berechtigungen vom Auth-Service abrufen
  const response = await fetch(
    `https://auth.palmdynamicx.de/api/permissions/users/${userId}/permissions/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-API-Key': apiKey
      }
    }
  );
  
  const data = await response.json();
  
  // Prüfe direkte Berechtigungen
  const directPermissions = data.direct_permissions || [];
  
  const vipPerm = directPermissions.find(p => 
    p.permission === 'vip_access' && 
    p.website?.id === websiteId &&
    p.granted &&
    (!p.expires_at || new Date(p.expires_at) > new Date())
  );
  
  return !!vipPerm;
}

// Verwendung:
if (await hasVIPAccess(userId, websiteId, token, apiKey)) {
  showVIPFeatures();
}
```

---

### Anwendungsfall 3: Explizite Verweigerung

**Szenario**: Ein Benutzer hat eine Rolle, soll aber eine spezifische Berechtigung NICHT haben

#### Im Auth-Service:
```
Benutzer: problem_user@example.com
  → Rolle: Blog Editor (hat "delete_article")
  
Aber: Diesem Benutzer soll Löschen verboten werden

→ Spezielle Berechtigung hinzufügen:
  Berechtigung: Artikel löschen (delete_article)
  Website: Blog Website
  Gewährt: ❌ NEIN  ← Explizite Verweigerung!
  Läuft ab: — (unbegrenzt)
```

#### Auf der Website prüfen:
```javascript
async function hasPermission(userId, permission, websiteId, token, apiKey) {
  // Berechtigungen vom Auth-Service abrufen
  const response = await fetch(
    `https://auth.palmdynamicx.de/api/permissions/users/${userId}/permissions/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-API-Key': apiKey
      }
    }
  );
  
  const data = await response.json();
  
  // 1. Prüfe explizite Verweigerungen (höchste Priorität!)
  const deniedPermissions = data.direct_permissions
    ?.filter(p => 
      !p.granted && 
      p.website?.id === websiteId &&
      p.permission === permission
    ) || [];
  
  if (deniedPermissions.length > 0) {
    return false; // Explizit verboten!
  }
  
  // 2. Prüfe normale Berechtigungen aus Rollen
  const hasRolePermission = data.roles.some(role => 
    (role.scope === 'global' || role.website?.id === websiteId) &&
    role.permissions.includes(permission)
  );
  
  return hasRolePermission;
}

// Ergebnis für problem_user@example.com:
await hasPermission(userId, 'edit_article', websiteId, token, apiKey);   // ✅ true (aus Rolle)
await hasPermission(userId, 'delete_article', websiteId, token, apiKey); // ❌ false (explizit verboten!)
```

---

## 🔍 Berechtigungen abfragen und prüfen

### API-Endpunkt: Benutzer-Berechtigungen abrufen

**Endpoint**: `GET /api/permissions/users/{user_id}/permissions/`  
**Auth**: Bearer Token erforderlich  
**Wo**: Auth-Service (`auth.palmdynamicx.de`)

**Request:**
```bash
curl -X GET https://auth.palmdynamicx.de/api/permissions/users/USER_ID/permissions/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "max@example.com",
    "username": "max"
  },
  "roles": [
    {
      "role": "Blog Editor",
      "scope": "local",
      "website": {
        "id": "blog-uuid",
        "name": "Blog Website"
      },
      "permissions": [
        "create_article",
        "edit_article",
        "delete_article"
      ]
    },
    {
      "role": "Support",
      "scope": "global",
      "website": null,
      "permissions": [
        "view_tickets",
        "reply_tickets"
      ]
    }
  ],
  "direct_permissions": [
    {
      "permission": "vip_access",
      "website": {
        "id": "premium-uuid",
        "name": "Premium Website"
      },
      "granted": true,
      "expires_at": "2026-01-31T23:59:59Z"
    }
  ]
}
```

---

### API-Endpunkt: Berechtigung prüfen

**Endpoint**: `POST /api/permissions/check/`  
**Auth**: Bearer Token erforderlich  
**Wo**: Auth-Service (`auth.palmdynamicx.de`)

**Request:**
```bash
curl -X POST https://auth.palmdynamicx.de/api/permissions/check/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "permission": "create_article",
    "website_id": "blog-uuid"
  }'
```

**Response:**
```json
{
  "has_permission": true,
  "permission": "create_article",
  "website_id": "blog-uuid",
  "granted_by": "role",
  "role_name": "Blog Editor"
}
```

**Verwendung auf Client-Website:**
```javascript
// Berechtigungsprüfung vom Auth-Service
async function checkPermission(permission, websiteId) {
  const response = await fetch(
    'https://auth.palmdynamicx.de/api/permissions/check/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        permission: permission,
        website_id: websiteId
      })
    }
  );
  
  const data = await response.json();
  return data.has_permission;
}

// Verwendung:
if (await checkPermission('create_article', 'blog-uuid')) {
  showCreateButton();
}
```

---

## 📊 Übersicht: Wo wird was gemacht?

| Aktion | Wo? | Wer? | Tool |
|--------|-----|------|------|
| **Berechtigungen definieren** | Auth-Service | Admin | Django Admin |
| **Rollen erstellen** | Auth-Service | Admin | Django Admin |
| **Rollen zuweisen** | Auth-Service | Admin | Django Admin |
| **Berechtigungen abrufen** | Auth-Service | Website | API GET /api/permissions/... |
| **Berechtigungen prüfen** | Auth-Service | Website | API POST /api/permissions/check/ |
| **Berechtigungen verwenden** | Client-Website | Developer | JWT Token + Code |
| **UI-Elemente steuern** | Client-Website | Developer | Frontend-Code |
| **API-Routen schützen** | Client-Website | Developer | Backend-Middleware |

---

## 💡 Best Practices

### ✅ DO (Machen):

1. **Berechtigungen im Auth-Service erstellen**
   - Alle Berechtigungen zentral verwalten
   - Aussagekräftige Codenamen verwenden
   - Beschreibungen hinzufügen

2. **Rollen für Benutzergruppen verwenden**
   - Nicht für jeden Benutzer einzelne Berechtigungen
   - Wiederverwendbare Rollen erstellen
   - Klare Rollennamen (z.B. "Blog Editor", "Shop Manager")

3. **Berechtigungen im Backend prüfen**
   - IMMER Berechtigungen auf dem Server prüfen
   - Frontend-Prüfung nur für UX (Button verstecken)
   - JWT Token verifizieren

4. **Global vs. Lokal klar trennen**
   - Systemweite Rechte = Global
   - Website-spezifische Rechte = Lokal
   - Nicht mischen!

5. **Mehrere Rollen kombinieren**
   - Ein Benutzer kann mehrere Rollen haben
   - Globale + Lokale Rollen möglich
   - Flexibel kombinierbar

### ❌ DON'T (Nicht machen):

1. **Keine Berechtigungen auf Client-Websites erstellen**
   - ❌ Alle Berechtigungen im Auth-Service!
   - ❌ Keine lokalen Berechtigungssysteme
   - ❌ Keine Duplikate

2. **Keine direkten Berechtigungen für normale Benutzer**
   - ❌ Nutze Rollen statt direkter Berechtigungen
   - ✅ Direkte Berechtigungen nur für Ausnahmen/Tests
   - ✅ Mit Ablaufdatum für temporäre Zugriffe

3. **Nicht nur im Frontend prüfen**
   - ❌ Frontend-Prüfung kann umgangen werden
   - ✅ IMMER auch Backend-Prüfung
   - ✅ Sicherheit auf Server-Seite

4. **Keine is_superuser vergeben**
   - ❌ Django Superuser nur für echte System-Admins
   - ✅ Nutze Rollen mit spezifischen Berechtigungen
   - ✅ Granulare Kontrolle

5. **Keine Django Groups verwenden**
   - ❌ Django Groups sind veraltet in diesem System
   - ✅ Nutze das Permissions System
   - ✅ Klare Hierarchie: Benutzer → Rollen → Berechtigungen

---

## 🚀 Quick Start Checkliste für KI-Agenten

Wenn du dieses System implementieren sollst, folge dieser Checkliste:

### Im Auth-Service (auth.palmdynamicx.de/admin):

- [ ] **1. Berechtigungen definieren**
  - [ ] Liste alle benötigten Berechtigungen auf
  - [ ] Vergib aussagekräftige Codenamen (z.B. `create_article`, `delete_user`)
  - [ ] Lege fest: Global oder Lokal?
  - [ ] Erstelle im Admin: Permissions System → Berechtigungen

- [ ] **2. Rollen erstellen**
  - [ ] Gruppiere Berechtigungen in logische Rollen
  - [ ] Erstelle im Admin: Permissions System → Rollen
  - [ ] Weise Berechtigungen zu Rollen zu

- [ ] **3. Benutzer zuweisen**
  - [ ] Öffne Benutzer im Admin
  - [ ] Scrolle zu "Rollen & Berechtigungen"
  - [ ] Klicke auf "+" und weise Rollen zu

### Auf der Client-Website:

- [ ] **4. Backend-Middleware implementieren**
  - [ ] Erstelle `requirePermission()` Middleware
  - [ ] JWT Token decodieren
  - [ ] Berechtigungen aus Token lesen
  - [ ] API-Routen schützen

- [ ] **5. Frontend-Components erstellen**
  - [ ] `usePermissions()` Hook/Composable erstellen
  - [ ] `CheckPermission` Component erstellen
  - [ ] UI-Elemente bedingt anzeigen
  - [ ] Buttons/Links verstecken ohne Berechtigung

- [ ] **6. Testen**
  - [ ] Login als Benutzer mit Rolle
  - [ ] Prüfe ob Berechtigungen im Token sind
  - [ ] Teste API-Aufrufe (sollten 403 bei fehlender Berechtigung)
  - [ ] Teste UI (Buttons sollten versteckt sein)

---

## 📖 Weiterführende Dokumentation

- **API-Endpunkte**: [API_ENDPOINTS_COMPLETE.md](./API_ENDPOINTS_COMPLETE.md)
- **Frontend-Integration**: [FRONTEND_PERMISSIONS.md](./FRONTEND_PERMISSIONS.md)
- **Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## ⚠️ Zusammenfassung für KI-Agenten

**WICHTIG ZU VERSTEHEN:**

1. **Berechtigungen werden IMMER im Auth-Service erstellt**
   - URL: `https://auth.palmdynamicx.de/admin/`
   - Nicht auf den Client-Websites!

2. **Berechtigungen werden auf Client-Websites VERWENDET**
   - JWT Token enthält alle Berechtigungen
   - Backend prüft Token
   - Frontend zeigt/versteckt UI-Elemente

3. **Workflow:**
   ```
   Auth-Service (ERSTELLEN)
     → Berechtigungen definieren
     → Rollen erstellen
     → Benutzer zuweisen
   
   Client-Website (VERWENDEN)
     → JWT Token empfangen
     → Token decodieren
     → Berechtigungen prüfen
     → Zugriff gewähren/verweigern
   ```

4. **Code-Beispiele in diesem Dokument zeigen:**
   - ✅ Wie Berechtigungen im Auth-Service erstellt werden
   - ✅ Wie Token-Inhalte aussehen
   - ✅ Wie Backend-Middleware aussieht
   - ✅ Wie Frontend-Components aussehen
   - ✅ Komplette Beispiele für verschiedene Use Cases

**Wenn du Berechtigungen implementieren sollst:**
1. Gehe zum Auth-Service Admin
2. Erstelle Berechtigungen + Rollen
3. Weise Benutzer zu
4. Implementiere Prüfung auf Client-Website

**Ende der Dokumentation** | Stand: Januar 2026 | Version 2.0
