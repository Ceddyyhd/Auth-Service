from rest_framework import serializers
from .models import Permission, Role, UserRole, UserPermission
from accounts.models import Website
from django.contrib.auth import get_user_model

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions."""
    
    website_name = serializers.CharField(source='website.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'description', 'scope', 
                  'website', 'website_name', 'created_at')
        read_only_fields = ('id', 'created_at')


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for roles."""
    
    website_name = serializers.CharField(source='website.name', read_only=True, allow_null=True)
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source='permissions',
        required=False
    )
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'scope', 'website', 
                  'website_name', 'permissions', 'permission_ids', 'created_at')
        read_only_fields = ('id', 'created_at')


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user role assignments."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True, allow_null=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = UserRole
        fields = ('id', 'user', 'user_email', 'role', 'role_name', 
                  'website', 'website_name', 'assigned_at', 
                  'assigned_by', 'assigned_by_email')
        read_only_fields = ('id', 'assigned_at', 'assigned_by')


class UserPermissionSerializer(serializers.ModelSerializer):
    """Serializer for direct user permission assignments."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True, allow_null=True)
    assigned_by_email = serializers.EmailField(source='assigned_by.email', read_only=True, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserPermission
        fields = ('id', 'user', 'user_email', 'permission', 'permission_name',
                  'website', 'website_name', 'granted', 'assigned_at',
                  'assigned_by', 'assigned_by_email', 'expires_at', 'is_active')
        read_only_fields = ('id', 'assigned_at', 'assigned_by', 'is_active')


class UserPermissionsListSerializer(serializers.Serializer):
    """Serializer for listing all effective permissions of a user."""
    
    user_id = serializers.UUIDField()
    user_email = serializers.EmailField()
    website_id = serializers.UUIDField(allow_null=True)
    website_name = serializers.CharField(allow_null=True)
    
    global_permissions = serializers.ListField(child=serializers.CharField())
    local_permissions = serializers.ListField(child=serializers.CharField())
    
    roles = serializers.ListField(child=serializers.CharField())
