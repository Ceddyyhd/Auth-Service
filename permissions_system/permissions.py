from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Permission, Role, UserRole, UserPermission

User = get_user_model()


class PermissionChecker:
    """
    Utility class to check user permissions.
    Handles both global and local (website-specific) permissions.
    """
    
    @staticmethod
    def get_user_permissions(user, website=None):
        """
        Get all effective permissions for a user.
        
        Args:
            user: User instance
            website: Website instance (optional)
        
        Returns:
            dict: Dictionary with 'global' and 'local' permission lists
        """
        permissions = {
            'global': set(),
            'local': set(),
        }
        
        # Superusers have all permissions
        if user.is_superuser:
            all_perms = Permission.objects.all()
            if website:
                permissions['global'] = set(
                    all_perms.filter(scope='global').values_list('codename', flat=True)
                )
                permissions['local'] = set(
                    all_perms.filter(scope='local', website=website).values_list('codename', flat=True)
                )
            else:
                permissions['global'] = set(
                    all_perms.filter(scope='global').values_list('codename', flat=True)
                )
            return permissions
        
        # Get permissions from roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        
        if website:
            # Include both global roles and website-specific roles
            user_roles = user_roles.filter(
                role__scope='global'
            ) | user_roles.filter(
                role__scope='local',
                website=website
            )
        
        for user_role in user_roles:
            role_perms = user_role.role.permissions.all()
            
            for perm in role_perms:
                if perm.scope == 'global':
                    permissions['global'].add(perm.codename)
                elif website and perm.website == website:
                    permissions['local'].add(perm.codename)
        
        # Get direct permissions
        direct_perms = UserPermission.objects.filter(
            user=user
        ).select_related('permission')
        
        if website:
            direct_perms = direct_perms.filter(
                permission__scope='global'
            ) | direct_perms.filter(
                permission__scope='local',
                website=website
            )
        
        for user_perm in direct_perms:
            # Skip expired permissions
            if not user_perm.is_active():
                continue
            
            perm = user_perm.permission
            
            # Handle explicit denials
            if not user_perm.granted:
                if perm.scope == 'global':
                    permissions['global'].discard(perm.codename)
                elif perm.scope == 'local':
                    permissions['local'].discard(perm.codename)
            else:
                if perm.scope == 'global':
                    permissions['global'].add(perm.codename)
                elif website and perm.website == website:
                    permissions['local'].add(perm.codename)
        
        return permissions
    
    @staticmethod
    def has_permission(user, permission_codename, website=None):
        """
        Check if user has a specific permission.
        
        Args:
            user: User instance
            permission_codename: String codename of the permission
            website: Website instance (optional)
        
        Returns:
            bool: True if user has the permission
        """
        if user.is_superuser:
            return True
        
        permissions = PermissionChecker.get_user_permissions(user, website)
        
        # Check in both global and local permissions
        return (
            permission_codename in permissions['global'] or
            permission_codename in permissions['local']
        )
    
    @staticmethod
    def has_any_permission(user, permission_codenames, website=None):
        """
        Check if user has any of the specified permissions.
        
        Args:
            user: User instance
            permission_codenames: List of permission codenames
            website: Website instance (optional)
        
        Returns:
            bool: True if user has at least one of the permissions
        """
        if user.is_superuser:
            return True
        
        permissions = PermissionChecker.get_user_permissions(user, website)
        all_user_perms = permissions['global'] | permissions['local']
        
        return any(perm in all_user_perms for perm in permission_codenames)
    
    @staticmethod
    def has_all_permissions(user, permission_codenames, website=None):
        """
        Check if user has all of the specified permissions.
        
        Args:
            user: User instance
            permission_codenames: List of permission codenames
            website: Website instance (optional)
        
        Returns:
            bool: True if user has all of the permissions
        """
        if user.is_superuser:
            return True
        
        permissions = PermissionChecker.get_user_permissions(user, website)
        all_user_perms = permissions['global'] | permissions['local']
        
        return all(perm in all_user_perms for perm in permission_codenames)
    
    @staticmethod
    def get_user_roles(user, website=None):
        """
        Get all roles assigned to a user.
        
        Args:
            user: User instance
            website: Website instance (optional)
        
        Returns:
            QuerySet: UserRole queryset
        """
        roles = UserRole.objects.filter(user=user)
        
        if website:
            roles = roles.filter(
                role__scope='global'
            ) | roles.filter(
                role__scope='local',
                website=website
            )
        
        return roles


# Convenience function for checking permissions in views
def user_has_permission(user, permission_codename, website=None):
    """
    Convenience function to check if a user has a specific permission.
    
    Usage:
        if user_has_permission(request.user, 'view_reports', website):
            # User has permission
    """
    return PermissionChecker.has_permission(user, permission_codename, website)
