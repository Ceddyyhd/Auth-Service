from django.urls import path
from .views import (
    PermissionListCreateView,
    PermissionDetailView,
    RoleListCreateView,
    RoleDetailView,
    UserRoleListView,
    AssignRoleToUserView,
    RevokeRoleFromUserView,
    UserPermissionListView,
    AssignPermissionToUserView,
    revoke_permission_from_user,
    check_user_permissions,
    check_specific_permission,
)

app_name = 'permissions_system'

urlpatterns = [
    # Permissions
    path('permissions/', PermissionListCreateView.as_view(), name='permission_list'),
    path('permissions/<uuid:pk>/', PermissionDetailView.as_view(), name='permission_detail'),
    
    # Roles
    path('roles/', RoleListCreateView.as_view(), name='role_list'),
    path('roles/<uuid:pk>/', RoleDetailView.as_view(), name='role_detail'),
    
    # User Role Assignments
    path('user-roles/', UserRoleListView.as_view(), name='user_role_list'),
    path('assign-role/', AssignRoleToUserView.as_view(), name='assign_role'),
    path('revoke-role/', RevokeRoleFromUserView.as_view(), name='revoke_role'),
    
    # User Permission Assignments
    path('user-permissions/', UserPermissionListView.as_view(), name='user_permission_list'),
    path('assign-permission/', AssignPermissionToUserView.as_view(), name='assign_permission'),
    path('revoke-permission/', revoke_permission_from_user, name='revoke_permission'),
    
    # Permission Checking
    path('check/<str:user_id>/', check_user_permissions, name='check_user_permissions'),
    path('check/me/', check_user_permissions, name='check_my_permissions'),
    path('check-permission/', check_specific_permission, name='check_specific_permission'),
]
