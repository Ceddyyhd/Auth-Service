"""
Custom Permission Backend for unified permission system.
Connects custom UserRole/UserPermission with Django Admin.
"""
from django.contrib.auth.backends import BaseBackend
from django.utils import timezone


class CustomPermissionBackend(BaseBackend):
    """
    Custom authentication backend that uses our UserRole and UserPermission system
    for Django Admin access control.
    """
    
    def authenticate(self, request, **kwargs):
        """We don't handle authentication, only permissions."""
        return None
    
    def has_perm(self, user_obj, perm, obj=None):
        """
        Check if user has a specific permission.
        Format: app_label.permission_codename (e.g., 'accounts.view_user')
        """
        if not user_obj or not user_obj.is_active:
            return False
        
        # Superusers always have all permissions
        if user_obj.is_superuser:
            return True
        
        # Staff users need to be checked against custom permissions
        if not user_obj.is_staff:
            return False
        
        # Import here to avoid circular imports
        from .models import UserPermission, UserRole
        
        # The permission codename can be in two formats:
        # 1. 'app_label.codename' (e.g., 'accounts.view_user')
        # 2. Just 'codename' (e.g., 'view_user')
        # Our database stores the full format with app_label, so we need to match accordingly
        
        # Check direct permissions (UserPermission)
        direct_perms = UserPermission.objects.filter(
            user=user_obj,
            permission__codename=perm,  # Match the full permission string
            granted=True
        ).select_related('permission')
        
        for user_perm in direct_perms:
            # Check if permission is expired
            if user_perm.is_active():
                return True
        
        # Check permissions via roles (UserRole)
        user_roles = UserRole.objects.filter(
            user=user_obj
        ).select_related('role').prefetch_related('role__permissions')
        
        for user_role in user_roles:
            # Check if any permission in this role matches
            for permission in user_role.role.permissions.all():
                if permission.codename == perm:
                    return True
        
        return False
    
    def has_module_perms(self, user_obj, app_label):
        """
        Check if user has any permissions for a given app.
        This determines if the app appears in Django Admin sidebar.
        """
        if not user_obj or not user_obj.is_active:
            return False
        
        # Superusers always have module permissions
        if user_obj.is_superuser:
            return True
        
        # Staff users need to be checked
        if not user_obj.is_staff:
            return False
        
        # Import here to avoid circular imports
        from .models import UserPermission, UserRole
        
        # Check if user has ANY permission (direct or via role)
        has_direct = UserPermission.objects.filter(
            user=user_obj,
            granted=True
        ).exists()
        
        has_role = UserRole.objects.filter(
            user=user_obj
        ).exists()
        
        # If user has any permissions at all, show all modules
        # (more fine-grained control can be added later)
        return has_direct or has_role
    
    def get_user_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings that the user has.
        """
        if not user_obj or not user_obj.is_active:
            return set()
        
        if user_obj.is_superuser:
            # Superusers have all permissions
            from django.contrib.auth.models import Permission as DjangoPermission
            return set(f"{p.content_type.app_label}.{p.codename}" 
                      for p in DjangoPermission.objects.all())
        
        if not user_obj.is_staff:
            return set()
        
        from .models import UserPermission, UserRole
        
        permissions = set()
        
        # Get direct permissions
        direct_perms = UserPermission.objects.filter(
            user=user_obj,
            granted=True
        ).select_related('permission')
        
        for user_perm in direct_perms:
            if user_perm.is_active():
                # Use the codename as-is (already includes app_label if present)
                permissions.add(user_perm.permission.codename)
        
        # Get permissions from roles
        user_roles = UserRole.objects.filter(
            user=user_obj
        ).select_related('role').prefetch_related('role__permissions')
        
        for user_role in user_roles:
            for permission in user_role.role.permissions.all():
                # Use the codename as-is (already includes app_label if present)
                permissions.add(permission.codename)
        
        return permissions
    
    def get_all_permissions(self, user_obj, obj=None):
        """
        Return all permissions the user has (including via roles).
        """
        return self.get_user_permissions(user_obj, obj)
    
    def get_group_permissions(self, user_obj, obj=None):
        """
        Return permissions from groups (in our case, roles).
        """
        if not user_obj or not user_obj.is_active:
            return set()
        
        if not user_obj.is_staff:
            return set()
        
        from .models import UserRole
        
        permissions = set()
        
        user_roles = UserRole.objects.filter(
            user=user_obj
        ).select_related('role').prefetch_related('role__permissions')
        
        for user_role in user_roles:
            for permission in user_role.role.permissions.all():
                # Use the codename as-is (already includes app_label if present)
                permissions.add(permission.codename)
        
        return permissions
