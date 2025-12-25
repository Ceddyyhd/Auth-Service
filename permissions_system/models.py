from django.db import models
from django.conf import settings
import uuid


class Permission(models.Model):
    """
    Represents a specific permission/right in the system.
    Can be global or local to a specific website.
    """
    
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('local', 'Lokal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Name')
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Codename',
        help_text='Eindeutiger Code für diese Berechtigung (z.B. "view_reports")'
    )
    description = models.TextField(blank=True, verbose_name='Beschreibung')
    
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default='local',
        verbose_name='Geltungsbereich'
    )
    
    # For local permissions
    website = models.ForeignKey(
        'accounts.Website',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='permissions',
        verbose_name='Website',
        help_text='Leer lassen für globale Berechtigungen'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')
    
    class Meta:
        verbose_name = 'Berechtigung'
        verbose_name_plural = 'Berechtigungen'
        ordering = ['scope', 'name']
        unique_together = [['codename', 'website']]
    
    def __str__(self):
        if self.scope == 'global':
            return f"{self.name} (Global)"
        return f"{self.name} ({self.website.name if self.website else 'Lokal'})"
    
    def clean(self):
        """Validate that global permissions don't have a website."""
        from django.core.exceptions import ValidationError
        if self.scope == 'global' and self.website:
            raise ValidationError('Globale Berechtigungen können nicht an eine Website gebunden sein.')
        if self.scope == 'local' and not self.website:
            raise ValidationError('Lokale Berechtigungen müssen an eine Website gebunden sein.')


class Role(models.Model):
    """
    Represents a role that groups multiple permissions.
    Roles are assigned to users via UserRole, where the global/local scope is defined.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name='Name')
    description = models.TextField(blank=True, verbose_name='Beschreibung')
    
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True,
        verbose_name='Berechtigungen'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Aktualisiert am')
    
    class Meta:
        verbose_name = 'Rolle'
        verbose_name_plural = 'Rollen'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Assigns roles to users with global or local scope.
    - Global: Role applies to all websites
    - Local: Role applies only to specified website(s)
    """
    
    SCOPE_CHOICES = [
        ('global', 'Global - Gilt für alle Websites'),
        ('local', 'Lokal - Nur für ausgewählte Website'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Benutzer'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        verbose_name='Rolle'
    )
    
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default='local',
        verbose_name='Geltungsbereich',
        help_text='Global = Alle Websites, Lokal = Nur ausgewählte Website'
    )
    
    # For local scope
    website = models.ForeignKey(
        'accounts.Website',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_role_assignments',
        verbose_name='Website',
        help_text='Pflicht wenn Geltungsbereich "Lokal" ist'
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Zugewiesen am')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_assignments_made',
        verbose_name='Zugewiesen von'
    )
    
    class Meta:
        verbose_name = 'Benutzerrolle'
        verbose_name_plural = 'Benutzerrollen'
        ordering = ['-assigned_at']
        unique_together = [['user', 'role', 'website']]
    
    def __str__(self):
        if self.scope == 'global':
            return f"{self.user.email} - {self.role.name} (Global)"
        if self.website:
            return f"{self.user.email} - {self.role.name} ({self.website.name})"
        return f"{self.user.email} - {self.role.name} (Lokal)"
    
    def clean(self):
        """Validate that local assignments have a website."""
        from django.core.exceptions import ValidationError
        if self.scope == 'global' and self.website:
            raise ValidationError('Globale Rollenzuweisungen können nicht an eine Website gebunden sein.')
        if self.scope == 'local' and not self.website:
            raise ValidationError('Lokale Rollenzuweisungen müssen an eine Website gebunden sein.')


class UserPermission(models.Model):
    """
    Direct assignment of permissions to users (bypass roles).
    Useful for special cases or temporary permissions.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_permissions_direct',
        verbose_name='Benutzer'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        verbose_name='Berechtigung'
    )
    
    # For additional context
    website = models.ForeignKey(
        'accounts.Website',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_permission_assignments',
        verbose_name='Website',
        help_text='Für lokale Berechtigungen'
    )
    
    granted = models.BooleanField(
        default=True,
        verbose_name='Gewährt',
        help_text='False = Explizite Verweigerung (überschreibt Rollenzuweisung)'
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Zugewiesen am')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_assignments_made',
        verbose_name='Zugewiesen von'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Läuft ab am',
        help_text='Optional: Temporäre Berechtigung'
    )
    
    class Meta:
        verbose_name = 'Benutzerberechtigung'
        verbose_name_plural = 'Benutzerberechtigungen'
        ordering = ['-assigned_at']
        unique_together = [['user', 'permission', 'website']]
    
    def __str__(self):
        status = "gewährt" if self.granted else "verweigert"
        if self.website:
            return f"{self.user.email} - {self.permission.name} ({status}, {self.website.name})"
        return f"{self.user.email} - {self.permission.name} ({status})"
    
    def is_active(self):
        """Check if permission is still active (not expired)."""
        if not self.expires_at:
            return True
        from django.utils import timezone
        return timezone.now() < self.expires_at
