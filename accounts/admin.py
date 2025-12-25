from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import AdminSite
from .models import User, Website, UserSession, SocialAccount, EmailVerificationToken, PasswordResetToken, MFADevice, SSOToken
from .admin_mfa import AdminMFAAuthenticationForm


class MFAAdminSite(AdminSite):
    """Custom Admin Site with MFA support"""
    site_header = "🔐 PalmDynamicX Auth Service Administration (MFA-geschützt)"
    site_title = "Auth Service Admin"
    index_title = "Willkommen im Auth Service Dashboard"
    login_form = AdminMFAAuthenticationForm
    login_template = 'admin/login.html'


# Ersetze die Standard-Admin-Site mit unserer MFA-geschützten Version
admin.site = MFAAdminSite()
admin.sites.site = admin.site


class UserRoleInline(admin.TabularInline):
    """Inline für Rollenzuweisung direkt im Benutzerprofil"""
    from permissions_system.models import UserRole
    model = UserRole
    fk_name = 'user'  # Wichtig: Wir bearbeiten vom User aus, nicht vom assigned_by
    extra = 1
    fields = ('role', 'website', 'assigned_at')
    readonly_fields = ('assigned_at',)
    verbose_name = 'Rollenzuweisung'
    verbose_name_plural = '🎭 Rollen & Berechtigungen'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "role":
            # Zeige globale und lokale Rollen
            from permissions_system.models import Role
            kwargs["queryset"] = Role.objects.all().order_by('scope', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class UserPermissionInline(admin.TabularInline):
    """Inline für direkte Berechtigungszuweisung"""
    from permissions_system.models import UserPermission
    model = UserPermission
    fk_name = 'user'  # Wichtig: Wir bearbeiten vom User aus, nicht vom assigned_by
    extra = 0
    fields = ('permission', 'website', 'granted', 'expires_at')
    verbose_name = 'Direkte Berechtigung'
    verbose_name_plural = '🔐 Spezielle Berechtigungen (optional)'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "permission":
            # Zeige alle Berechtigungen
            from permissions_system.models import Permission
            kwargs["queryset"] = Permission.objects.all().order_by('scope', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SocialAccountInline(admin.TabularInline):
    """Inline für verlinkte Social Accounts"""
    model = SocialAccount
    extra = 0
    fields = ('provider', 'email', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'Social Account'
    verbose_name_plural = '🔗 Verlinkte Social Accounts'
    can_delete = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'profile_completed', 
                    'is_active', 'is_staff', 'is_verified', 'get_roles_count', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_verified', 'profile_completed', 
                   'allowed_websites', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'company')
    ordering = ('-date_joined',)
    
    inlines = [UserRoleInline, UserPermissionInline, SocialAccountInline]
    
    fieldsets = (
        ('🔐 Login Informationen', {
            'fields': ('email', 'username', 'password')
        }),
        ('👤 Persönliche Informationen', {
            'fields': ('first_name', 'last_name', 'phone', 'date_of_birth', 'company')
        }),
        ('📍 Adresse', {
            'fields': ('street', 'street_number', 'city', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('⚙️ System-Berechtigungen', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified'),
            'description': '⚠️ System-Berechtigungen nur für Admin-Zugang. Verwende Rollen für normale Berechtigungen.'
        }),
        ('🌐 Website Zugriff', {
            'fields': ('allowed_websites',),
            'description': 'Auf welche Websites darf dieser Benutzer zugreifen?'
        }),
        ('📊 Status', {
            'fields': ('profile_completed', 'last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Neuen Benutzer erstellen', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name')
        }),
        ('Initiale Einstellungen', {
            'fields': ('is_staff', 'is_active', 'allowed_websites')
        }),
    )
    
    filter_horizontal = ('allowed_websites',)
    
    def get_roles_count(self, obj):
        """Zeigt Anzahl der zugewiesenen Rollen"""
        count = obj.user_roles.count()
        if count > 0:
            return f"✅ {count} Rolle(n)"
        return "❌ Keine Rollen"
    get_roles_count.short_description = 'Rollen'
    
    # Entferne Django's default groups und permissions
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Verstecke die verwirrenden Django groups/permissions
        if 'groups' in form.base_fields:
            del form.base_fields['groups']
        if 'user_permissions' in form.base_fields:
            del form.base_fields['user_permissions']
        return form


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'is_active', 'get_users_count', 
                    'get_roles_count', 'get_permissions_count', 'created_at')
    list_filter = ('is_active', 'auto_register_users', 'require_address', 
                   'require_phone', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('api_key', 'api_secret', 'client_id', 'client_secret', 'created_at', 'updated_at')
    
    fieldsets = (
        ('🌐 Allgemeine Informationen', {
            'fields': ('name', 'domain', 'callback_url', 'allowed_origins')
        }),
        ('🔑 API Credentials', {
            'fields': ('api_key', 'api_secret', 'client_id', 'client_secret'),
            'classes': ('collapse',),
            'description': '⚠️ Diese Credentials werden für die API-Integration benötigt. API Secret nur einmal kopieren!'
        }),
        ('⚙️ Einstellungen', {
            'fields': ('is_active', 'auto_register_users', 'require_email_verification')
        }),
        ('📝 Pflichtfelder bei Registrierung', {
            'fields': ('require_first_name', 'require_last_name', 'require_phone',
                      'require_address', 'require_date_of_birth', 'require_company'),
            'description': 'Wähle, welche Felder bei der Registrierung auf dieser Website erforderlich sind'
        }),
        ('📅 Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_users_count(self, obj):
        """Anzahl Benutzer mit Zugriff auf diese Website"""
        count = obj.users.count()
        if count > 0:
            return f"👥 {count}"
        return "—"
    get_users_count.short_description = 'Benutzer'
    
    def get_roles_count(self, obj):
        """Anzahl lokaler Rollen für diese Website"""
        count = obj.roles.count()
        if count > 0:
            return f"🎭 {count}"
        return "—"
    get_roles_count.short_description = 'Rollen'
    
    def get_permissions_count(self, obj):
        """Anzahl lokaler Berechtigungen für diese Website"""
        count = obj.permissions.count()
        if count > 0:
            return f"🔑 {count}"
        return "—"
    get_permissions_count.short_description = 'Berechtigungen'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'website', 'ip_address', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active', 'website', 'created_at')
    search_fields = ('user__email', 'website__name', 'ip_address')
    readonly_fields = ('created_at', 'last_activity')
    
    fieldsets = (
        ('Session Informationen', {'fields': ('user', 'website', 'is_active')}),
        ('Verbindungsdetails', {'fields': ('ip_address', 'user_agent')}),
        ('Zeitstempel', {'fields': ('created_at', 'last_activity', 'expires_at')}),
    )


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'email', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__email', 'email', 'provider_user_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Account Informationen', {
            'fields': ('user', 'provider', 'provider_user_id', 'email')
        }),
        ('Profildaten', {
            'fields': ('first_name', 'last_name', 'avatar_url')
        }),
        ('Zusätzliche Daten', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_preview', 'created_at', 'expires_at', 'is_used', 'is_token_valid')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('id', 'token', 'created_at', 'expires_at')
    
    fieldsets = (
        ('Benutzer', {'fields': ('user',)}),
        ('Token', {'fields': ('id', 'token', 'is_used')}),
        ('Zeitstempel', {'fields': ('created_at', 'expires_at')}),
    )
    
    def token_preview(self, obj):
        """Show shortened token for security."""
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token (Preview)'
    
    def is_token_valid(self, obj):
        """Show if token is still valid."""
        return obj.is_valid()
    is_token_valid.boolean = True
    is_token_valid.short_description = 'Gültig'


@admin.register(SSOToken)
class SSOTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'website', 'token_preview', 'created_at', 'expires_at', 'is_used', 'is_token_valid', 'ip_address')
    list_filter = ('is_used', 'website', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__username', 'website__name', 'token', 'ip_address')
    readonly_fields = ('id', 'token', 'created_at', 'expires_at', 'used_at', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('SSO Information', {'fields': ('id', 'user', 'website')}),
        ('Token', {'fields': ('token', 'is_used', 'used_at')}),
        ('Zeitstempel', {'fields': ('created_at', 'expires_at')}),
        ('Client Information', {'fields': ('ip_address', 'user_agent')}),
    )
    
    def token_preview(self, obj):
        """Show shortened token for security."""
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token (Preview)'
    
    def is_token_valid(self, obj):
        """Show if token is still valid."""
        return obj.is_valid()
    is_token_valid.boolean = True
    is_token_valid.short_description = 'Gültig'
    
    def has_add_permission(self, request):
        """Prevent manual creation - should only be created through SSO flow."""
        return False


@admin.register(MFADevice)
class MFADeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'secret_preview', 'created_at', 'activated_at', 'last_used', 'backup_codes_remaining')
    list_filter = ('is_active', 'created_at', 'activated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('id', 'secret_key', 'created_at', 'activated_at', 'last_used', 'backup_codes_display')
    
    fieldsets = (
        ('Benutzer', {'fields': ('user',)}),
        ('MFA Status', {'fields': ('id', 'is_active', 'activated_at', 'last_used')}),
        ('TOTP Secret', {
            'fields': ('secret_key',),
            'description': 'Base32-kodierter TOTP Secret Key. Nicht weitergeben!'
        }),
        ('Backup Codes', {
            'fields': ('backup_codes_display',),
            'description': 'Verbleibende Backup-Codes für Notfälle'
        }),
        ('Zeitstempel', {'fields': ('created_at',)}),
    )
    
    def secret_preview(self, obj):
        """Show shortened secret for security."""
        return f"{obj.secret_key[:8]}...{obj.secret_key[-4:]}"
    secret_preview.short_description = 'Secret (Preview)'
    
    def backup_codes_remaining(self, obj):
        """Show number of remaining backup codes."""
        return len(obj.get_backup_codes())
    backup_codes_remaining.short_description = 'Backup Codes'
    
    def backup_codes_display(self, obj):
        """Display backup codes as list."""
        codes = obj.get_backup_codes()
        if not codes:
            return "Keine Backup-Codes verfügbar"
        return "\n".join([f"{i+1}. {code}" for i, code in enumerate(codes)])
    backup_codes_display.short_description = 'Verbleibende Backup-Codes'
    
    def has_add_permission(self, request):
        """Prevent manual creation - should only be created through API."""
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_preview', 'created_at', 'expires_at', 'is_used', 'is_token_valid')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('id', 'token', 'created_at', 'expires_at')
    
    fieldsets = (
        ('Benutzer', {'fields': ('user',)}),
        ('Token', {'fields': ('id', 'token', 'is_used')}),
        ('Zeitstempel', {'fields': ('created_at', 'expires_at')}),
    )
    
    def token_preview(self, obj):
        """Show shortened token for security."""
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token (Preview)'
    
    def is_token_valid(self, obj):
        """Show if token is still valid."""
        return obj.is_valid()
    is_token_valid.boolean = True
    is_token_valid.short_description = 'Gültig'

