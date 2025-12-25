"""
Django Admin MFA (Multi-Factor Authentication) Support
Adds TOTP-based two-factor authentication to Django Admin login
"""
from django.contrib.auth import get_backends
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import MFADevice


class AdminMFAAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form for Django Admin with MFA support
    """
    mfa_token = forms.CharField(
        label=_("MFA Token (falls aktiviert)"),
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '6-stelliger Code',
            'autocomplete': 'off',
            'class': 'vTextField',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
        }),
        help_text=_("Geben Sie den 6-stelligen Code aus Ihrer Authenticator-App ein, falls MFA aktiviert ist.")
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        mfa_token = self.cleaned_data.get('mfa_token')
        
        if username is not None and password:
            # First, authenticate with username and password
            self.user_cache = self.get_user_from_credentials(username, password)
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            
            # Check if user has MFA enabled
            try:
                mfa_device = MFADevice.objects.get(user=self.user_cache, is_active=True)
                
                # MFA is enabled, token is required
                if not mfa_token:
                    raise ValidationError(
                        _("Multi-Factor Authentication ist für diesen Account aktiviert. "
                          "Bitte geben Sie den 6-stelligen Code aus Ihrer Authenticator-App ein."),
                        code='mfa_required',
                    )
                
                # Verify MFA token
                if not mfa_device.verify_token(mfa_token):
                    raise ValidationError(
                        _("Der eingegebene MFA-Code ist ungültig oder abgelaufen. "
                          "Bitte versuchen Sie es erneut."),
                        code='invalid_mfa',
                    )
                
                # MFA verification successful
                
            except MFADevice.DoesNotExist:
                # No MFA device, proceed without MFA
                pass
            
            self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
    
    def get_user_from_credentials(self, username, password):
        """
        Authenticate user with username and password using Django's authentication backends
        """
        from django.contrib.auth import authenticate
        
        # Try to authenticate
        user = authenticate(self.request, username=username, password=password)
        
        # If not found by username, try email
        if user is None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(self.request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        return user


class AdminMFABackend(ModelBackend):
    """
    Custom authentication backend for Django Admin with MFA support.
    This backend extends the default ModelBackend to include MFA verification.
    """
    
    def authenticate(self, request, username=None, password=None, mfa_token=None, **kwargs):
        """
        Authenticate user with optional MFA token verification
        """
        # First authenticate with username/password using parent method
        user = super().authenticate(request, username=username, password=password, **kwargs)
        
        if user is None:
            return None
        
        # If this is an admin login request and user has MFA enabled
        if request and hasattr(request, 'path') and '/admin/login' in request.path:
            try:
                mfa_device = MFADevice.objects.get(user=user, is_active=True)
                
                # MFA is enabled - token verification is required
                # Note: The actual verification is handled in the form
                # This backend just ensures the user can proceed if MFA passes
                
                return user
                
            except MFADevice.DoesNotExist:
                # No MFA device, proceed without MFA check
                return user
        
        return user
