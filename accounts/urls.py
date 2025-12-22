from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    WebsiteListCreateView,
    WebsiteDetailView,
    UserWebsiteAccessView,
    verify_access,
    UserSessionListView,
)
from .social_views import (
    SocialLoginView,
    CompleteProfileView,
    CheckProfileCompletionView,
    get_social_accounts,
    unlink_social_account,
    get_website_required_fields,
)
from .email_views import (
    ResendVerificationEmailView,
    VerifyEmailView,
    RequestPasswordResetView,
    ResetPasswordView,
    test_smtp_configuration,
    get_smtp_configuration,
)
from .mfa_views import (
    EnableMFAView,
    VerifyMFASetupView,
    DisableMFAView,
    RegenerateBackupCodesView,
    get_mfa_status,
    verify_mfa_token,
)
from .sso_views import (
    initiate_sso,
    exchange_sso_token,
    check_sso_status,
    sso_login_callback,
    sso_logout,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email Verification
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    
    # Password Reset
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    # SMTP Configuration
    path('test-smtp/', test_smtp_configuration, name='test_smtp'),
    path('smtp-config/', get_smtp_configuration, name='smtp_config'),
    
    # Multi-Factor Authentication (MFA)
    path('mfa/enable/', EnableMFAView.as_view(), name='mfa_enable'),
    path('mfa/verify-setup/', VerifyMFASetupView.as_view(), name='mfa_verify_setup'),
    path('mfa/disable/', DisableMFAView.as_view(), name='mfa_disable'),
    path('mfa/backup-codes/', RegenerateBackupCodesView.as_view(), name='mfa_regenerate_backup_codes'),
    path('mfa/status/', get_mfa_status, name='mfa_status'),
    path('mfa/verify/', verify_mfa_token, name='mfa_verify_token'),
    
    # Single Sign-On (SSO)
    path('sso/initiate/', initiate_sso, name='sso_initiate'),
    path('sso/exchange/', exchange_sso_token, name='sso_exchange'),
    path('sso/status/', check_sso_status, name='sso_status'),
    path('sso/callback/', sso_login_callback, name='sso_callback'),
    path('sso/logout/', sso_logout, name='sso_logout'),
    
    # Social Login
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    path('social-accounts/', get_social_accounts, name='social_accounts'),
    path('social-accounts/<str:provider>/', unlink_social_account, name='unlink_social_account'),
    
    # Profile Completion
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
    path('check-profile-completion/', CheckProfileCompletionView.as_view(), name='check_profile_completion'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Websites
    path('websites/', WebsiteListCreateView.as_view(), name='website_list'),
    path('websites/<uuid:pk>/', WebsiteDetailView.as_view(), name='website_detail'),
    path('websites/<uuid:website_id>/required-fields/', get_website_required_fields, name='website_required_fields'),
    
    # Access Management
    path('users/<uuid:user_id>/websites/', UserWebsiteAccessView.as_view(), name='user_website_access'),
    path('verify-access/', verify_access, name='verify_access'),
    
    # Sessions
    path('sessions/', UserSessionListView.as_view(), name='session_list'),
]
