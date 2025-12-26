from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
import secrets
import pyotp
import json


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email as the unique identifier.
    Supports multi-website authentication.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='E-Mail')
    username = models.CharField(max_length=150, unique=True, verbose_name='Benutzername')
    
    # Personal Information
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Vorname')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Nachname')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    
    # Address Information
    street = models.CharField(max_length=255, blank=True, verbose_name='Straße')
    street_number = models.CharField(max_length=20, blank=True, verbose_name='Hausnummer')
    city = models.CharField(max_length=100, blank=True, verbose_name='Stadt')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='PLZ')
    country = models.CharField(max_length=100, blank=True, verbose_name='Land')
    
    # Additional Information
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Geburtsdatum')
    company = models.CharField(max_length=255, blank=True, verbose_name='Firma')
    
    # Lexware Integration
    lexware_contact_id = models.UUIDField(
        null=True, 
        blank=True, 
        verbose_name='Lexware Kontakt-ID',
        help_text='UUID des Kontakts in Lexware'
    )
    lexware_customer_number = models.IntegerField(
        null=True, 
        blank=True, 
        unique=True,
        verbose_name='Lexware Kundennummer',
        help_text='Eindeutige Kundennummer aus Lexware'
    )
    
    # Profile Completion
    profile_completed = models.BooleanField(default=False, verbose_name='Profil vollständig')
    
    # Status fields
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    is_staff = models.BooleanField(default=False, verbose_name='Staff-Status')
    is_verified = models.BooleanField(default=False, verbose_name='E-Mail verifiziert')
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Registriert am')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Letzter Login')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')
    
    # Multi-Website Support
    allowed_websites = models.ManyToManyField(
        'Website',
        blank=True,
        related_name='users',
        verbose_name='Erlaubte Websites'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Benutzer'
        verbose_name_plural = 'Benutzer'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Return the short name."""
        return self.first_name or self.username
    
    def has_website_access(self, website):
        """Check if user has access to a specific website."""
        if self.is_superuser:
            return True
        return self.allowed_websites.filter(id=website.id).exists()
    
    def is_ready_for_lexware(self):
        """Prüft ob Benutzerdaten vollständig genug für Lexware-Kontakt sind.
        
        PFLICHTFELDER:
        - E-Mail
        - Vor- UND Nachname
        - Vollständige Adresse (Straße, Stadt, PLZ)
        """
        # E-Mail ist Pflicht
        if not self.email:
            return False
        
        # Vor- UND Nachname sind Pflicht
        if not self.first_name or not self.first_name.strip():
            return False
        if not self.last_name or not self.last_name.strip():
            return False
        
        # Vollständige Adresse ist Pflicht
        if not self.street or not self.street.strip():
            return False
        if not self.city or not self.city.strip():
            return False
        if not self.postal_code or not self.postal_code.strip():
            return False
        
        return True
    
    def get_lexware_missing_fields(self):
        """Gibt Liste der fehlenden Felder für Lexware-Kontakt zurück."""
        missing = []
        
        if not self.email:
            missing.append('E-Mail')
        
        if not self.first_name or not self.first_name.strip():
            missing.append('Vorname')
        if not self.last_name or not self.last_name.strip():
            missing.append('Nachname')
        
        if not self.street or not self.street.strip():
            missing.append('Straße')
        if not self.city or not self.city.strip():
            missing.append('Stadt')
        if not self.postal_code or not self.postal_code.strip():
            missing.append('PLZ')
        
        return missing


class Website(models.Model):
    """
    Represents a website/application that uses this auth service.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name='Name')
    domain = models.CharField(max_length=255, unique=True, verbose_name='Domain')
    callback_url = models.URLField(verbose_name='Callback URL')
    allowed_origins = models.JSONField(
        default=list,
        verbose_name='Erlaubte Origins',
        help_text='Liste von erlaubten Origins für CORS (z.B. ["https://example.com"])'
    )
    
    # API Credentials
    api_key = models.CharField(
        max_length=64, 
        unique=True, 
        blank=True,
        verbose_name='API Key',
        help_text='Öffentlicher API Key für Client-seitige Anfragen'
    )
    api_secret = models.CharField(
        max_length=64, 
        blank=True,
        verbose_name='API Secret',
        help_text='Geheimer API Key - NUR für Server-seitige Anfragen!'
    )
    client_id = models.CharField(
        max_length=255, 
        unique=True, 
        blank=True,
        verbose_name='Client ID',
        help_text='OAuth2 Client ID für SSO'
    )
    client_secret = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Client Secret',
        help_text='OAuth2 Client Secret für SSO'
    )
    
    # Settings
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    auto_register_users = models.BooleanField(
        default=False,
        verbose_name='Automatische Benutzerregistrierung',
        help_text='Erlaubt neuen Benutzern automatischen Zugang zu dieser Website'
    )
    
    # Required Registration Fields
    require_first_name = models.BooleanField(default=False, verbose_name='Vorname erforderlich')
    require_last_name = models.BooleanField(default=False, verbose_name='Nachname erforderlich')
    require_phone = models.BooleanField(default=False, verbose_name='Telefon erforderlich')
    require_address = models.BooleanField(default=False, verbose_name='Adresse erforderlich')
    require_date_of_birth = models.BooleanField(default=False, verbose_name='Geburtsdatum erforderlich')
    require_company = models.BooleanField(default=False, verbose_name='Firma erforderlich')
    require_email_verification = models.BooleanField(default=False, verbose_name='E-Mail-Verifizierung erforderlich')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')
    
    class Meta:
        verbose_name = 'Website'
        verbose_name_plural = 'Websites'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.domain})"
    
    def save(self, *args, **kwargs):
        """Generate API keys and client credentials if not set."""
        if not self.api_key:
            self.api_key = f"pk_{secrets.token_urlsafe(32)}"
        if not self.api_secret:
            self.api_secret = f"sk_{secrets.token_urlsafe(32)}"
        if not self.client_id:
            self.client_id = f"client_{secrets.token_urlsafe(32)}"
        if not self.client_secret:
            self.client_secret = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)
    
    def regenerate_api_keys(self):
        """Regenerate API credentials (use with caution!)."""
        self.api_key = f"pk_{secrets.token_urlsafe(32)}"
        self.api_secret = f"sk_{secrets.token_urlsafe(32)}"
        self.client_id = f"client_{secrets.token_urlsafe(32)}"
        self.client_secret = secrets.token_urlsafe(48)
        self.save()
        return f"{self.name} ({self.domain})"


class UserSession(models.Model):
    """
    Tracks user sessions across different websites.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='sessions')
    
    # Session data
    ip_address = models.GenericIPAddressField(verbose_name='IP-Adresse')
    user_agent = models.TextField(verbose_name='User Agent')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Letzte Aktivität')
    expires_at = models.DateTimeField(verbose_name='Läuft ab am')
    
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    
    class Meta:
        verbose_name = 'Benutzersitzung'
        verbose_name_plural = 'Benutzersitzungen'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.website.name}"
    
    def is_expired(self):
        """Check if session is expired."""
        return timezone.now() > self.expires_at


class SocialAccount(models.Model):
    """
    Stores social login accounts (Google, Facebook, etc.).
    """
    
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('github', 'GitHub'),
        ('microsoft', 'Microsoft'),
        ('apple', 'Apple'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, verbose_name='Anbieter')
    provider_user_id = models.CharField(max_length=255, verbose_name='Provider User ID')
    
    # Additional data from provider
    email = models.EmailField(verbose_name='E-Mail vom Provider')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Vorname')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Nachname')
    avatar_url = models.URLField(blank=True, verbose_name='Profilbild URL')
    
    # Metadata
    extra_data = models.JSONField(default=dict, verbose_name='Zusätzliche Daten')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')
    
    class Meta:
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
        unique_together = [['provider', 'provider_user_id']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_provider_display()}"


class EmailVerificationToken(models.Model):
    """
    Token for email verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification token for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid."""
        return not self.is_used and timezone.now() < self.expires_at
    
    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)


class SSOToken(models.Model):
    """
    SSO Token for cross-website authentication.
    Allows users to be automatically logged in across all websites.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sso_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='sso_tokens', 
                                help_text='Website requesting SSO')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Token expiry time (short-lived)')
    is_used = models.BooleanField(default=False, help_text='Whether token has been exchanged')
    used_at = models.DateTimeField(null=True, blank=True, help_text='When token was used')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'SSO Token'
        verbose_name_plural = 'SSO Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['user', 'website']),
        ]
    
    def __str__(self):
        return f"SSO Token for {self.user.email} → {self.website.name}"
    
    def is_valid(self):
        """Check if token is still valid."""
        return (
            not self.is_used 
            and timezone.now() < self.expires_at
        )
    
    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    @staticmethod
    def generate_token():
        """Generate a secure random SSO token."""
        return secrets.token_urlsafe(32)


class MFADevice(models.Model):
    """
    Multi-Factor Authentication device for a user.
    Supports TOTP (Time-based One-Time Password) authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa_device')
    secret_key = models.CharField(max_length=32, help_text='Base32 encoded TOTP secret')
    is_active = models.BooleanField(default=False, help_text='Whether MFA is enabled for this user')
    backup_codes = models.TextField(blank=True, help_text='JSON-encoded list of backup codes')
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True, help_text='When MFA was first activated')
    last_used = models.DateTimeField(null=True, blank=True, help_text='Last time MFA was successfully used')
    
    class Meta:
        verbose_name = 'MFA Device'
        verbose_name_plural = 'MFA Devices'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"MFA for {self.user.email} ({status})"
    
    @staticmethod
    def generate_secret():
        """Generate a new TOTP secret key."""
        return pyotp.random_base32()
    
    def get_totp(self):
        """Get TOTP instance for this device."""
        return pyotp.TOTP(self.secret_key)
    
    def verify_token(self, token):
        """
        Verify a TOTP token or backup code.
        Returns True if valid, False otherwise.
        """
        # Remove any spaces from token
        token = token.replace(' ', '').replace('-', '')
        
        # Try TOTP verification first
        totp = self.get_totp()
        if totp.verify(token, valid_window=1):  # Allow 1 time step tolerance
            self.last_used = timezone.now()
            self.save(update_fields=['last_used'])
            return True
        
        # Try backup codes if TOTP failed
        if self.verify_backup_code(token):
            return True
        
        return False
    
    def get_backup_codes(self):
        """Get list of backup codes."""
        if not self.backup_codes:
            return []
        try:
            return json.loads(self.backup_codes)
        except json.JSONDecodeError:
            return []
    
    def set_backup_codes(self, codes):
        """Set backup codes (list of strings)."""
        self.backup_codes = json.dumps(codes)
    
    def verify_backup_code(self, code):
        """
        Verify and consume a backup code.
        Returns True if valid, False otherwise.
        """
        codes = self.get_backup_codes()
        if code in codes:
            # Remove the used code
            codes.remove(code)
            self.set_backup_codes(codes)
            self.last_used = timezone.now()
            self.save(update_fields=['backup_codes', 'last_used'])
            return True
        return False
    
    @staticmethod
    def generate_backup_codes(count=10):
        """Generate a list of backup codes."""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()  # 8 hex characters
            codes.append(code)
        return codes
    
    def get_provisioning_uri(self, issuer_name='Auth Service'):
        """
        Get the provisioning URI for QR code generation.
        """
        totp = self.get_totp()
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name=issuer_name
        )


class PasswordResetToken(models.Model):
    """
    Token for password reset.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"
    
    def is_valid(self):
        """Check if token is still valid."""
        return not self.is_used and timezone.now() < self.expires_at
    
    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

