from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from accounts.models import Website
from .models import Permission, Role, UserRole, UserPermission
from .serializers import (
    PermissionSerializer,
    RoleSerializer,
    UserRoleSerializer,
    UserPermissionSerializer,
    UserPermissionsListSerializer
)
from .permissions import PermissionChecker

User = get_user_model()


# Permission Views
class PermissionListCreateView(generics.ListCreateAPIView):
    """
    📋 Berechtigungen verwalten
    
    **GET** - Liste aller Berechtigungen abrufen
    **POST** - Neue Berechtigung erstellen
    
    ## Query Parameter (GET):
    - `website` (UUID, optional): Nur Berechtigungen für diese Website
    - `scope` (string, optional): Filter nach 'global' oder 'local'
    
    ## Beispiel GET:
    ```
    GET /api/permissions/permissions/?scope=global
    Authorization: Bearer {access_token}
    ```
    
    **Response:**
    ```json
    [
      {
        "id": "uuid",
        "name": "Artikel erstellen",
        "codename": "create_article",
        "description": "Erlaubt das Erstellen von Artikeln",
        "scope": "local",
        "website": "uuid",
        "created_at": "2025-12-22T10:00:00Z"
      }
    ]
    ```
    
    ## Beispiel POST:
    ```json
    {
      "name": "Artikel erstellen",
      "codename": "create_article",
      "description": "Erlaubt das Erstellen von Blog-Artikeln",
      "scope": "local",
      "website": "uuid"
    }
    ```
    
    **Scope Erklärung:**
    - `global`: Gilt für alle Websites (website muss null/leer sein)
    - `local`: Gilt nur für eine Website (website erforderlich)
    
    **Berechtigung erforderlich:** Admin-Rechte
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter permissions by website if provided."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website')
        scope = self.request.query_params.get('scope')
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if scope:
            queryset = queryset.filter(scope=scope)
        
        return queryset


class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    📝 Einzelne Berechtigung verwalten
    
    **GET** - Berechtigung abrufen
    **PUT/PATCH** - Berechtigung aktualisieren
    **DELETE** - Berechtigung löschen
    
    ## Beispiel GET:
    ```
    GET /api/permissions/permissions/{uuid}/
    Authorization: Bearer {access_token}
    ```
    
    ## Beispiel PUT:
    ```json
    {
      "name": "Artikel erstellen und bearbeiten",
      "codename": "create_edit_article",
      "description": "Erweiterte Berechtigung",
      "scope": "local",
      "website": "uuid"
    }
    ```
    
    **Berechtigung erforderlich:** Admin-Rechte
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]


# Role Views
class RoleListCreateView(generics.ListCreateAPIView):
    """
    🎭 Rollen verwalten
    
    **GET** - Liste aller Rollen abrufen
    **POST** - Neue Rolle erstellen
    
    ## Query Parameter (GET):
    - `website` (UUID, optional): Nur Rollen für diese Website
    - `scope` (string, optional): Filter nach 'global' oder 'local'
    
    ## Beispiel GET:
    ```
    GET /api/permissions/roles/?scope=local&website={uuid}
    Authorization: Bearer {access_token}
    ```
    
    **Response:**
    ```json
    [
      {
        "id": "uuid",
        "name": "Blog Editor",
        "description": "Kann Artikel erstellen und bearbeiten",
        "scope": "local",
        "website": "uuid",
        "permissions": ["uuid1", "uuid2"],
        "created_at": "2025-12-22T10:00:00Z"
      }
    ]
    ```
    
    ## Beispiel POST - Globale Rolle:
    ```json
    {
      "name": "Super Admin",
      "description": "Voller Zugriff auf alle Websites",
      "scope": "global",
      "permissions": [
        "permission-uuid-1",
        "permission-uuid-2"
      ]
    }
    ```
    
    ## Beispiel POST - Lokale Rolle:
    ```json
    {
      "name": "Blog Editor",
      "description": "Editor für Blog-Website",
      "scope": "local",
      "website": "website-uuid",
      "permissions": [
        "create-article-permission-uuid",
        "edit-article-permission-uuid"
      ]
    }
    ```
    
    **Wichtig:** Eine Rolle bündelt mehrere Berechtigungen!
    
    **Berechtigung erforderlich:** Admin-Rechte
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter roles by website if provided."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website')
        scope = self.request.query_params.get('scope')
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if scope:
            queryset = queryset.filter(scope=scope)
        
        return queryset


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a role.
    
    GET /api/permissions/roles/{id}/
    PUT /api/permissions/roles/{id}/
    DELETE /api/permissions/roles/{id}/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


# User Role Assignment Views
class UserRoleListView(generics.ListAPIView):
    """
    List all user role assignments.
    
    GET /api/permissions/user-roles/
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by user or website if provided."""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        website_id = self.request.query_params.get('website')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        return queryset


class AssignRoleToUserView(APIView):
    """
    👤 Rolle an Benutzer zuweisen
    
    Weise einem Benutzer eine Rolle zu. Der Benutzer erhält damit alle
    Berechtigungen dieser Rolle.
    
    ## Beispiel - Globale Rolle zuweisen:
    ```json
    POST /api/permissions/assign-role/
    Authorization: Bearer {access_token}
    
    {
      "user_id": "user-uuid",
      "role_id": "super-admin-role-uuid"
    }
    ```
    
    ## Beispiel - Lokale Rolle zuweisen:
    ```json
    {
      "user_id": "user-uuid",
      "role_id": "blog-editor-role-uuid",
      "website_id": "website-uuid"
    }
    ```
    
    **Response:**
    ```json
    {
      "message": "Rolle 'Blog Editor' wurde user@example.com zugewiesen.",
      "data": {
        "id": "assignment-uuid",
        "user": "user-uuid",
        "role": "role-uuid",
        "website": "website-uuid",
        "assigned_at": "2025-12-22T10:00:00Z"
      }
    }
    ```
    
    **Mehrfach-Zuweisung:** Ein Benutzer kann mehrere Rollen haben!
    - Beispiel: "Support" (global) + "Editor" (lokal, Website A) + "Manager" (lokal, Website B)
    
    **Berechtigung erforderlich:** Admin-Rechte
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        website_id = request.data.get('website_id')
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            website = None
            
            if website_id:
                website = Website.objects.get(id=website_id)
            
            # Validate scope
            if role.scope == 'local' and not website:
                return Response({
                    'error': 'Lokale Rollen benötigen eine Website.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or get the assignment
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                website=website,
                defaults={'assigned_by': request.user}
            )
            
            if created:
                return Response({
                    'message': f'Rolle "{role.name}" wurde {user.email} zugewiesen.',
                    'data': UserRoleSerializer(user_role).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Rolle bereits zugewiesen.',
                    'data': UserRoleSerializer(user_role).data
                }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Benutzer nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Role.DoesNotExist:
            return Response({'error': 'Rolle nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Website.DoesNotExist:
            return Response({'error': 'Website nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)


class RevokeRoleFromUserView(APIView):
    """
    Revoke a role from a user.
    
    POST /api/permissions/revoke-role/
    Body: {
        "user_id": "uuid",
        "role_id": "uuid",
        "website_id": "uuid" (optional)
    }
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        website_id = request.data.get('website_id')
        
        try:
            filters = {
                'user_id': user_id,
                'role_id': role_id,
            }
            
            if website_id:
                filters['website_id'] = website_id
            
            user_role = UserRole.objects.get(**filters)
            role_name = user_role.role.name
            user_email = user_role.user.email
            
            user_role.delete()
            
            return Response({
                'message': f'Rolle "{role_name}" wurde von {user_email} entfernt.'
            }, status=status.HTTP_200_OK)
        
        except UserRole.DoesNotExist:
            return Response({
                'error': 'Rollenzuweisung nicht gefunden.'
            }, status=status.HTTP_404_NOT_FOUND)


# User Permission Assignment Views
class UserPermissionListView(generics.ListAPIView):
    """
    List all direct user permission assignments.
    
    GET /api/permissions/user-permissions/
    """
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter by user or website if provided."""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        website_id = self.request.query_params.get('website')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        return queryset


class AssignPermissionToUserView(APIView):
    """
    Assign a permission directly to a user.
    
    POST /api/permissions/assign-permission/
    Body: {
        "user_id": "uuid",
        "permission_id": "uuid",
        "website_id": "uuid" (optional),
        "granted": true/false,
        "expires_at": "2024-12-31T23:59:59Z" (optional)
    }
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        permission_id = request.data.get('permission_id')
        website_id = request.data.get('website_id')
        granted = request.data.get('granted', True)
        expires_at = request.data.get('expires_at')
        
        try:
            user = User.objects.get(id=user_id)
            permission = Permission.objects.get(id=permission_id)
            website = None
            
            if website_id:
                website = Website.objects.get(id=website_id)
            
            # Validate scope
            if permission.scope == 'local' and not website:
                return Response({
                    'error': 'Lokale Berechtigungen benötigen eine Website.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or update the assignment
            user_perm, created = UserPermission.objects.update_or_create(
                user=user,
                permission=permission,
                website=website,
                defaults={
                    'granted': granted,
                    'assigned_by': request.user,
                    'expires_at': expires_at
                }
            )
            
            action = "gewährt" if granted else "verweigert"
            
            return Response({
                'message': f'Berechtigung "{permission.name}" wurde {user.email} {action}.',
                'data': UserPermissionSerializer(user_perm).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'Benutzer nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Permission.DoesNotExist:
            return Response({'error': 'Berechtigung nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Website.DoesNotExist:
            return Response({'error': 'Website nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def revoke_permission_from_user(request):
    """
    Revoke a permission from a user.
    
    POST /api/permissions/revoke-permission/
    Body: {
        "user_id": "uuid",
        "permission_id": "uuid",
        "website_id": "uuid" (optional)
    }
    """
    user_id = request.data.get('user_id')
    permission_id = request.data.get('permission_id')
    website_id = request.data.get('website_id')
    
    try:
        filters = {
            'user_id': user_id,
            'permission_id': permission_id,
        }
        
        if website_id:
            filters['website_id'] = website_id
        
        user_perm = UserPermission.objects.get(**filters)
        perm_name = user_perm.permission.name
        user_email = user_perm.user.email
        
        user_perm.delete()
        
        return Response({
            'message': f'Berechtigung "{perm_name}" wurde von {user_email} entfernt.'
        }, status=status.HTTP_200_OK)
    
    except UserPermission.DoesNotExist:
        return Response({
            'error': 'Berechtigungszuweisung nicht gefunden.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_user_permissions(request, user_id=None):
    """
    🔍 Benutzer-Berechtigungen prüfen
    
    Ruft ALLE effektiven Berechtigungen eines Benutzers ab - sowohl aus
    Rollen als auch direkt zugewiesene Berechtigungen.
    
    ## Eigene Berechtigungen prüfen:
    ```
    GET /api/permissions/check/me/?website_id={uuid}
    Authorization: Bearer {access_token}
    ```
    
    ## Andere Benutzer prüfen (nur Admins):
    ```
    GET /api/permissions/check/{user_id}/?website_id={uuid}
    Authorization: Bearer {admin_access_token}
    ```
    
    **Query Parameter:**
    - `website_id` (UUID, optional): Filtert lokale Berechtigungen für diese Website
    
    **Response:**
    ```json
    {
      "user_id": "uuid",
      "user_email": "user@example.com",
      "website_id": "website-uuid",
      "website_name": "Meine Website",
      "global_permissions": [
        "manage_users",
        "view_system_logs"
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
    
    **Verwendung im Frontend:**
    ```javascript
    // Berechtigungen laden
    const response = await fetch('/api/permissions/check/me/?website_id=xxx', {
      headers: { 'Authorization': 'Bearer token' }
    });
    const data = await response.json();
    
    // UI basierend auf Berechtigungen
    const allPermissions = [
      ...data.global_permissions,
      ...data.local_permissions
    ];
    
    if (allPermissions.includes('create_article')) {
      showCreateButton();
    }
    ```
    
    **Berechtigung erforderlich:** 
    - Eigene Berechtigungen: Angemeldet
    - Andere Benutzer: Admin-Rechte
    """
    # Allow users to check their own permissions
    if user_id == 'me' or user_id is None:
        user = request.user
    else:
        # Only admins can check other users' permissions
        if not request.user.is_staff:
            return Response({
                'error': 'Sie haben keine Berechtigung, die Berechtigungen anderer Benutzer zu prüfen.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, id=user_id)
    
    website_id = request.query_params.get('website_id')
    website = None
    
    if website_id:
        website = get_object_or_404(Website, id=website_id)
    
    # Get permissions
    permissions = PermissionChecker.get_user_permissions(user, website)
    roles = PermissionChecker.get_user_roles(user, website)
    
    response_data = {
        'user_id': str(user.id),
        'user_email': user.email,
        'website_id': str(website.id) if website else None,
        'website_name': website.name if website else None,
        'global_permissions': list(permissions['global']),
        'local_permissions': list(permissions['local']),
        'roles': [role.role.name for role in roles]
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_specific_permission(request):
    """
    ✅ Spezifische Berechtigung prüfen
    
    Prüft ob der aktuelle Benutzer eine bestimmte Berechtigung hat.
    Schneller als alle Berechtigungen abzurufen wenn man nur eine prüfen will.
    
    ## Beispiel Request:
    ```json
    POST /api/permissions/check-permission/
    Authorization: Bearer {access_token}
    
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
      "website_id": "website-uuid",
      "has_permission": true
    }
    ```
    
    ## Verwendung vor Aktionen:
    ```javascript
    // Vor dem Erstellen eines Artikels prüfen
    async function createArticle() {
      const check = await fetch('/api/permissions/check-permission/', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer token',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          permission_codename: 'create_article',
          website_id: websiteId
        })
      });
      
      const result = await check.json();
      
      if (result.has_permission) {
        // Artikel erstellen...
      } else {
        alert('Keine Berechtigung!');
      }
    }
    ```
    
    **Body Parameter:**
    - `permission_codename` (string, erforderlich): Codename der Berechtigung
    - `website_id` (UUID, optional): Für lokale Berechtigungen
    
    **Berechtigung erforderlich:** Angemeldet
    """
    permission_codename = request.data.get('permission_codename')
    website_id = request.data.get('website_id')
    
    if not permission_codename:
        return Response({
            'error': 'permission_codename ist erforderlich.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    website = None
    if website_id:
        website = get_object_or_404(Website, id=website_id)
    
    has_permission = PermissionChecker.has_permission(
        request.user,
        permission_codename,
        website
    )
    
    return Response({
        'user_id': str(request.user.id),
        'user_email': request.user.email,
        'permission_codename': permission_codename,
        'website_id': str(website.id) if website else None,
        'has_permission': has_permission
    }, status=status.HTTP_200_OK)
