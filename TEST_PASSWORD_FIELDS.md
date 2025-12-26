# ✅ Password Field Kompatibilität

## Problem gelöst!

Die API akzeptiert jetzt **beide Feldnamen** für Passwort-Bestätigungen:

### Bei Registrierung:
- ✅ `password2` (interner Name)
- ✅ `password_confirm` (dokumentierter Name)

### Bei Passwort-Änderung:
- ✅ `new_password2` (interner Name)
- ✅ `new_password_confirm` (dokumentierter Name)

## Testing

### Test 1: Registrierung mit `password_confirm`
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "website_id": "your-website-uuid"
  }'
```

### Test 2: Registrierung mit `password2`
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "username": "testuser2",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "website_id": "your-website-uuid"
  }'
```

### Test 3: Passwort ändern mit `new_password_confirm`
```bash
curl -X POST http://localhost:8000/api/accounts/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password": "TestPass123!",
    "new_password": "NewPass123!",
    "new_password_confirm": "NewPass123!"
  }'
```

### Test 4: Passwort ändern mit `new_password2`
```bash
curl -X POST http://localhost:8000/api/accounts/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password": "TestPass123!",
    "new_password": "NewPass123!",
    "new_password2": "NewPass123!"
  }'
```

## Implementierung

### Serializer-Logik:

```python
# UserRegistrationSerializer
def validate(self, attrs):
    # Support both password2 and password_confirm
    password_confirm = attrs.pop('password_confirm', None)
    if password_confirm:
        attrs['password2'] = password_confirm
    
    if not attrs.get('password2'):
        raise serializers.ValidationError({
            "password2": "Passwort-Bestätigung ist erforderlich."
        })
    
    if attrs['password'] != attrs['password2']:
        raise serializers.ValidationError({
            "password": "Passwörter stimmen nicht überein."
        })
    return attrs
```

```python
# ChangePasswordSerializer
def validate(self, attrs):
    # Support both new_password2 and new_password_confirm
    new_password_confirm = attrs.pop('new_password_confirm', None)
    if new_password_confirm:
        attrs['new_password2'] = new_password_confirm
    
    if not attrs.get('new_password2'):
        raise serializers.ValidationError({
            "new_password2": "Passwort-Bestätigung ist erforderlich."
        })
    
    if attrs['new_password'] != attrs['new_password2']:
        raise serializers.ValidationError({
            "new_password": "Neue Passwörter stimmen nicht überein."
        })
    return attrs
```

## Frontend Beispiele

### JavaScript (beide Varianten funktionieren):

```javascript
// Variante 1: Mit password_confirm (dokumentiert)
await fetch('/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'SecurePass123!',
    password_confirm: 'SecurePass123!',  // ✅ Funktioniert
    website_id: 'uuid'
  })
});

// Variante 2: Mit password2 (intern)
await fetch('/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'SecurePass123!',
    password2: 'SecurePass123!',  // ✅ Funktioniert auch
    website_id: 'uuid'
  })
});
```

### Python Client (beide Varianten):

```python
import requests

# Variante 1: password_confirm
response = requests.post(
    'http://localhost:8000/api/accounts/register/',
    json={
        'email': 'user@example.com',
        'username': 'user123',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!',  # ✅
        'website_id': 'uuid'
    }
)

# Variante 2: password2
response = requests.post(
    'http://localhost:8000/api/accounts/register/',
    json={
        'email': 'user@example.com',
        'username': 'user123',
        'password': 'SecurePass123!',
        'password2': 'SecurePass123!',  # ✅
        'website_id': 'uuid'
    }
)
```

## Vorteile

1. ✅ **Rückwärtskompatibilität**: Alter Code mit `password2` funktioniert weiter
2. ✅ **Dokumentations-Konformität**: Neuer Code kann `password_confirm` verwenden
3. ✅ **Flexibilität**: Beide Varianten werden akzeptiert
4. ✅ **Klare Fehlermeldungen**: Beide Feldnamen werden in Validierung berücksichtigt
5. ✅ **Keine Breaking Changes**: Existierende Integrationen brechen nicht

## Dokumentation aktualisiert

- ✅ [API_REFERENCE.md](API_REFERENCE.md) - Zeigt beide Varianten
- ✅ [EMAIL_SYSTEM.md](EMAIL_SYSTEM.md) - Beispiele aktualisiert
- ✅ Swagger/OpenAPI - Beide Felder dokumentiert

---

Alle Endpoints akzeptieren jetzt beide Feldnamen! 🎉
