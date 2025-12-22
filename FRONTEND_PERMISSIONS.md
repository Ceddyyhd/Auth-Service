# 🔑 Berechtigungen im Frontend/Panel abrufen

## 📡 API Endpoints

### 1. Alle Berechtigungen des aktuellen Benutzers abrufen

```http
GET /api/permissions/check/me/?website_id={website_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "user_id": "uuid",
  "user_email": "user@example.com",
  "website_id": "uuid",
  "website_name": "Meine Website",
  "global_permissions": [
    "view_system_logs",
    "manage_users"
  ],
  "local_permissions": [
    "create_article",
    "edit_article",
    "delete_article"
  ],
  "roles": [
    "Super Admin",
    "Blog Editor"
  ]
}
```

### 2. Spezifische Berechtigung prüfen

```http
POST /api/permissions/check-permission/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "permission_codename": "create_article",
  "website_id": "uuid"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "user_email": "user@example.com",
  "permission_codename": "create_article",
  "website_id": "uuid",
  "has_permission": true
}
```

---

## 💻 JavaScript/TypeScript Integration

### React/Vue/Angular Beispiel

```typescript
// services/permissions.service.ts

class PermissionsService {
  private baseUrl = 'http://localhost:8000/api/permissions';
  
  /**
   * Hole alle Berechtigungen für aktuelle Website
   */
  async getUserPermissions(websiteId: string): Promise<UserPermissions> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(
      `${this.baseUrl}/check/me/?website_id=${websiteId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Fehler beim Laden der Berechtigungen');
    }
    
    return await response.json();
  }
  
  /**
   * Prüfe spezifische Berechtigung
   */
  async hasPermission(
    permissionCode: string, 
    websiteId?: string
  ): Promise<boolean> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(
      `${this.baseUrl}/check-permission/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          permission_codename: permissionCode,
          website_id: websiteId
        })
      }
    );
    
    const data = await response.json();
    return data.has_permission;
  }
  
  /**
   * Prüfe mehrere Berechtigungen auf einmal
   */
  async checkMultiplePermissions(
    permissions: string[],
    websiteId?: string
  ): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {};
    
    // Parallel prüfen für bessere Performance
    await Promise.all(
      permissions.map(async (perm) => {
        results[perm] = await this.hasPermission(perm, websiteId);
      })
    );
    
    return results;
  }
}

export const permissionsService = new PermissionsService();

// Types
interface UserPermissions {
  user_id: string;
  user_email: string;
  website_id: string | null;
  website_name: string | null;
  global_permissions: string[];
  local_permissions: string[];
  roles: string[];
}
```

---

## 🎨 React Hook für Berechtigungen

```typescript
// hooks/usePermissions.ts
import { useState, useEffect } from 'react';
import { permissionsService } from '../services/permissions.service';

export function usePermissions(websiteId: string) {
  const [permissions, setPermissions] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPermissions();
  }, [websiteId]);

  async function loadPermissions() {
    try {
      setLoading(true);
      const data = await permissionsService.getUserPermissions(websiteId);
      
      // Kombiniere global und lokal
      const allPermissions = [
        ...data.global_permissions,
        ...data.local_permissions
      ];
      
      setPermissions(allPermissions);
      setRoles(data.roles);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function hasPermission(permissionCode: string): boolean {
    return permissions.includes(permissionCode);
  }

  function hasAnyPermission(permissionCodes: string[]): boolean {
    return permissionCodes.some(code => permissions.includes(code));
  }

  function hasAllPermissions(permissionCodes: string[]): boolean {
    return permissionCodes.every(code => permissions.includes(code));
  }

  function hasRole(roleName: string): boolean {
    return roles.includes(roleName);
  }

  return {
    permissions,
    roles,
    loading,
    error,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    reload: loadPermissions
  };
}
```

---

## 🚀 Verwendung in React Komponenten

### Beispiel 1: Bedingte UI-Elemente

```tsx
// components/ArticlePanel.tsx
import React from 'react';
import { usePermissions } from '../hooks/usePermissions';

function ArticlePanel() {
  const websiteId = 'your-website-uuid';
  const { hasPermission, loading } = usePermissions(websiteId);

  if (loading) {
    return <div>Lade Berechtigungen...</div>;
  }

  return (
    <div className="article-panel">
      <h1>Artikel Verwaltung</h1>
      
      {hasPermission('create_article') && (
        <button onClick={() => createArticle()}>
          ➕ Neuer Artikel
        </button>
      )}
      
      {hasPermission('edit_article') && (
        <button onClick={() => editArticle()}>
          ✏️ Bearbeiten
        </button>
      )}
      
      {hasPermission('delete_article') && (
        <button onClick={() => deleteArticle()}>
          🗑️ Löschen
        </button>
      )}
      
      {!hasPermission('create_article') && (
        <p className="no-permission">
          ⚠️ Keine Berechtigung zum Erstellen von Artikeln
        </p>
      )}
    </div>
  );
}
```

### Beispiel 2: Protected Route

```tsx
// components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { usePermissions } from '../hooks/usePermissions';

interface Props {
  children: React.ReactNode;
  requiredPermission?: string;
  requiredRole?: string;
  websiteId: string;
}

function ProtectedRoute({ 
  children, 
  requiredPermission, 
  requiredRole,
  websiteId 
}: Props) {
  const { hasPermission, hasRole, loading } = usePermissions(websiteId);

  if (loading) {
    return <div>Lade...</div>;
  }

  // Prüfe Berechtigung
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/no-permission" />;
  }

  // Prüfe Rolle
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/no-permission" />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
```

### Beispiel 3: Menü basierend auf Berechtigungen

```tsx
// components/AdminMenu.tsx
import { usePermissions } from '../hooks/usePermissions';

function AdminMenu({ websiteId }) {
  const { hasPermission, hasAnyPermission } = usePermissions(websiteId);

  const menuItems = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      show: true // Immer sichtbar
    },
    {
      label: 'Artikel',
      path: '/articles',
      icon: '📝',
      show: hasAnyPermission(['create_article', 'edit_article', 'view_article'])
    },
    {
      label: 'Benutzer',
      path: '/users',
      icon: '👥',
      show: hasPermission('manage_users')
    },
    {
      label: 'Einstellungen',
      path: '/settings',
      icon: '⚙️',
      show: hasPermission('change_settings')
    },
    {
      label: 'Logs',
      path: '/logs',
      icon: '📋',
      show: hasPermission('view_system_logs')
    }
  ];

  return (
    <nav className="admin-menu">
      {menuItems.filter(item => item.show).map(item => (
        <a key={item.path} href={item.path}>
          {item.icon} {item.label}
        </a>
      ))}
    </nav>
  );
}
```

---

## 🔒 Higher-Order Component (HOC)

```tsx
// hoc/withPermission.tsx
import React from 'react';
import { usePermissions } from '../hooks/usePermissions';

export function withPermission(
  Component: React.ComponentType<any>,
  requiredPermission: string,
  websiteId: string
) {
  return function PermissionWrapper(props: any) {
    const { hasPermission, loading } = usePermissions(websiteId);

    if (loading) {
      return <div>Lade...</div>;
    }

    if (!hasPermission(requiredPermission)) {
      return (
        <div className="no-permission">
          <h2>🔒 Keine Berechtigung</h2>
          <p>Sie benötigen die Berechtigung "{requiredPermission}"</p>
        </div>
      );
    }

    return <Component {...props} />;
  };
}

// Verwendung:
const AdminPanel = withPermission(
  AdminPanelComponent,
  'manage_users',
  'website-uuid'
);
```

---

## 🎯 Vue.js Beispiel

```typescript
// composables/usePermissions.ts (Vue 3 Composition API)
import { ref, onMounted } from 'vue';
import { permissionsService } from '@/services/permissions.service';

export function usePermissions(websiteId: string) {
  const permissions = ref<string[]>([]);
  const roles = ref<string[]>([]);
  const loading = ref(true);
  const error = ref<string | null>(null);

  async function loadPermissions() {
    try {
      loading.value = true;
      const data = await permissionsService.getUserPermissions(websiteId);
      
      permissions.value = [
        ...data.global_permissions,
        ...data.local_permissions
      ];
      roles.value = data.roles;
      error.value = null;
    } catch (err: any) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  }

  function hasPermission(permissionCode: string): boolean {
    return permissions.value.includes(permissionCode);
  }

  onMounted(() => {
    loadPermissions();
  });

  return {
    permissions,
    roles,
    loading,
    error,
    hasPermission,
    reload: loadPermissions
  };
}
```

```vue
<!-- components/ArticlePanel.vue -->
<template>
  <div class="article-panel">
    <h1>Artikel Verwaltung</h1>
    
    <button v-if="hasPermission('create_article')" @click="createArticle">
      ➕ Neuer Artikel
    </button>
    
    <button v-if="hasPermission('edit_article')" @click="editArticle">
      ✏️ Bearbeiten
    </button>
    
    <div v-if="!hasPermission('create_article')" class="no-permission">
      ⚠️ Keine Berechtigung
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePermissions } from '@/composables/usePermissions';

const websiteId = 'your-website-uuid';
const { hasPermission, loading } = usePermissions(websiteId);

function createArticle() {
  // ...
}

function editArticle() {
  // ...
}
</script>
```

---

## 📱 Vanilla JavaScript Beispiel

```javascript
// permissions-manager.js

class PermissionsManager {
  constructor(websiteId) {
    this.websiteId = websiteId;
    this.permissions = [];
    this.roles = [];
  }

  async init() {
    await this.loadPermissions();
    this.updateUI();
  }

  async loadPermissions() {
    const token = localStorage.getItem('access_token');
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/permissions/check/me/?website_id=${this.websiteId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      const data = await response.json();
      this.permissions = [
        ...data.global_permissions,
        ...data.local_permissions
      ];
      this.roles = data.roles;
    } catch (error) {
      console.error('Fehler beim Laden der Berechtigungen:', error);
    }
  }

  hasPermission(permissionCode) {
    return this.permissions.includes(permissionCode);
  }

  updateUI() {
    // Zeige/Verstecke Elemente basierend auf Berechtigungen
    document.querySelectorAll('[data-permission]').forEach(element => {
      const requiredPermission = element.getAttribute('data-permission');
      
      if (this.hasPermission(requiredPermission)) {
        element.style.display = '';
      } else {
        element.style.display = 'none';
      }
    });
  }
}

// Verwendung:
const permManager = new PermissionsManager('website-uuid');
permManager.init();
```

```html
<!-- HTML mit data-permission Attributen -->
<div class="admin-panel">
  <button data-permission="create_article">
    Neuer Artikel
  </button>
  
  <button data-permission="edit_article">
    Bearbeiten
  </button>
  
  <button data-permission="delete_article">
    Löschen
  </button>
  
  <div data-permission="view_system_logs">
    <h2>System Logs</h2>
    <!-- Nur für Admins sichtbar -->
  </div>
</div>
```

---

## 🎨 CSS für Berechtigungs-Feedback

```css
/* styles/permissions.css */

.no-permission {
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 15px;
  border-radius: 5px;
  margin: 10px 0;
}

.has-permission {
  opacity: 1;
  pointer-events: auto;
}

.no-permission-disabled {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
}

[data-permission]:not(.has-permission) {
  display: none;
}
```

---

## 💡 Best Practices

### 1. **Cache Berechtigungen**
```typescript
// Mit Cache für bessere Performance
class PermissionsCache {
  private cache = new Map<string, CacheEntry>();
  private ttl = 5 * 60 * 1000; // 5 Minuten

  async getPermissions(websiteId: string) {
    const cached = this.cache.get(websiteId);
    
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data;
    }

    const data = await permissionsService.getUserPermissions(websiteId);
    
    this.cache.set(websiteId, {
      data,
      timestamp: Date.now()
    });

    return data;
  }

  invalidate(websiteId?: string) {
    if (websiteId) {
      this.cache.delete(websiteId);
    } else {
      this.cache.clear();
    }
  }
}
```

### 2. **Fehlerbehandlung**
```typescript
try {
  const hasPermission = await permissionsService.hasPermission('create_article');
  if (hasPermission) {
    // Aktion ausführen
  } else {
    showError('Keine Berechtigung');
  }
} catch (error) {
  if (error.status === 401) {
    // Token abgelaufen - neu einloggen
    redirectToLogin();
  } else {
    showError('Fehler beim Prüfen der Berechtigung');
  }
}
```

### 3. **Server-seitige Validierung nicht vergessen!**
```typescript
// Frontend-Check ist für UX, aber IMMER auch Backend prüfen!
if (hasPermission('delete_article')) {
  try {
    await api.deleteArticle(articleId);
    // Server hat auch geprüft
  } catch (error) {
    // Server hat Zugriff verweigert
    showError('Keine Berechtigung');
  }
}
```

---

## 🚀 Schnellstart

1. **Berechtigungen laden beim Login:**
```typescript
async function handleLogin(email, password) {
  const tokens = await authService.login(email, password);
  localStorage.setItem('access_token', tokens.access);
  
  // Sofort Berechtigungen laden
  const permissions = await permissionsService.getUserPermissions(websiteId);
  // Speichere in State/Store
  store.setPermissions(permissions);
}
```

2. **Berechtigungen prüfen bevor Aktion:**
```typescript
async function createArticle() {
  if (!hasPermission('create_article')) {
    showError('Keine Berechtigung zum Erstellen von Artikeln');
    return;
  }
  
  // Artikel erstellen...
}
```

3. **UI automatisch aktualisieren:**
```typescript
// React/Vue watcht automatisch
// Vanilla JS: Event-System
window.addEventListener('permissions-updated', () => {
  updateUI();
});
```

---

**Viel Erfolg! 🎉**
