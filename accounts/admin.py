from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from .models import User, Website, UserSession, SocialAccount, EmailVerificationToken, PasswordResetToken, MFADevice, SSOToken, APIRequestLog
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
    fields = ('role', 'scope', 'website', 'assigned_at')
    readonly_fields = ('assigned_at',)
    verbose_name = 'Rollenzuweisung'
    verbose_name_plural = '🎭 Rollen & Berechtigungen'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "role":
            # Zeige alle Rollen
            from permissions_system.models import Role
            kwargs["queryset"] = Role.objects.all().order_by('name')
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
            kwargs["queryset"] = Permission.objects.all().order_by('website', 'name')
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
                    'is_active', 'is_staff', 'is_verified', 'get_roles_count', 
                    'lexware_customer_number', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_verified', 'profile_completed', 
                   'allowed_websites', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'company',
                    'lexware_customer_number')
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
        ('💼 Lexware Integration', {
            'fields': ('lexware_contact_id', 'lexware_customer_number'),
            'classes': ('collapse',),
            'description': '🔗 Automatisch synchronisiert mit Lexware bei Registrierung'
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
    
    readonly_fields = ('lexware_contact_id', 'lexware_customer_number')
    
    def get_roles_count(self, obj):
        """Zeigt Anzahl der zugewiesenen Rollen"""
        count = obj.user_roles.count()
        if count > 0:
            return f"✅ {count} Rolle(n)"
        return "❌ Keine Rollen"
    get_roles_count.short_description = 'Rollen'
    
    # Actions für Lexware-Integration
    actions = ['sync_with_lexware', 'update_lexware_contacts']
    
    def sync_with_lexware(self, request, queryset):
        """Erstellt Lexware-Kontakte für ausgewählte Benutzer ohne Kontakt"""
        from .lexware_integration import get_lexware_client, LexwareAPIError
        
        users_without_contact = queryset.filter(lexware_contact_id__isnull=True)
        
        if not users_without_contact.exists():
            self.message_user(request, "Alle ausgewählten Benutzer haben bereits einen Lexware-Kontakt.", 'warning')
            return
        
        lexware = get_lexware_client()
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for user in users_without_contact:
            # Validiere Daten
            is_valid, error_msg = lexware.validate_user_data(user)
            
            if not is_valid:
                self.message_user(
                    request, 
                    f"⊘ {user.email} übersprungen: {error_msg}", 
                    'warning'
                )
                skipped_count += 1
                continue
            
            try:
                lexware.create_customer_contact(user)
                success_count += 1
            except (LexwareAPIError, Exception) as e:
                error_count += 1
                self.message_user(request, f"✗ Fehler bei {user.email}: {str(e)}", 'error')
        
        if success_count > 0:
            self.message_user(
                request, 
                f"✓ {success_count} Lexware-Kontakt(e) erfolgreich erstellt.", 
                'success'
            )
        
        if skipped_count > 0:
            self.message_user(
                request,
                f"⊘ {skipped_count} Benutzer übersprungen (unvollständige Daten).",
                'warning'
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"✗ {error_count} Fehler beim Erstellen von Kontakten.",
                'error'
            )
    
    sync_with_lexware.short_description = "🔗 Lexware-Kontakte für ausgewählte Benutzer erstellen"
    
    def update_lexware_contacts(self, request, queryset):
        """Aktualisiert bestehende Lexware-Kontakte für ausgewählte Benutzer"""
        from .lexware_integration import get_lexware_client, LexwareAPIError
        
        users_with_contact = queryset.filter(lexware_contact_id__isnull=False)
        
        if not users_with_contact.exists():
            self.message_user(request, "Keiner der ausgewählten Benutzer hat einen Lexware-Kontakt.", 'warning')
            return
        
        lexware = get_lexware_client()
        success_count = 0
        error_count = 0
        
        for user in users_with_contact:
            try:
                lexware.update_customer_contact(user)
                success_count += 1
            except (LexwareAPIError, Exception) as e:
                error_count += 1
                self.message_user(request, f"Fehler bei {user.email}: {str(e)}", 'error')
        
        if success_count > 0:
            self.message_user(
                request,
                f"✓ {success_count} Lexware-Kontakt(e) erfolgreich aktualisiert.",
                'success'
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"✗ {error_count} Fehler beim Aktualisieren von Kontakten.",
                'error'
            )
    
    update_lexware_contacts.short_description = "🔄 Lexware-Kontakte für ausgewählte Benutzer aktualisieren"
    
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
    
    def get_readonly_fields(self, request, obj=None):
        """API Credentials nur beim Bearbeiten readonly, nicht beim Erstellen."""
        if obj:  # Bearbeiten
            return ('api_key', 'api_secret', 'client_id', 'client_secret', 'created_at', 'updated_at')
        return ('created_at', 'updated_at')  # Erstellen - API Keys werden automatisch generiert
    
    def get_fieldsets(self, request, obj=None):
        """Passe Fieldsets an abhängig davon ob wir erstellen oder bearbeiten."""
        if obj:  # Bearbeiten - zeige API Credentials
            return (
                ('🌐 Allgemeine Informationen', {
                    'fields': ('name', 'domain', 'callback_url', 'allowed_origins')
                }),
                ('🔑 API Credentials', {
                    'fields': ('api_key', 'api_secret', 'client_id', 'client_secret'),
                    'classes': ('collapse',),
                    'description': '⚠️ Diese Credentials werden automatisch generiert. API Secret nur einmal kopieren!'
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
        else:  # Erstellen - verstecke API Credentials
            return (
                ('🌐 Allgemeine Informationen', {
                    'fields': ('name', 'domain', 'callback_url', 'allowed_origins'),
                    'description': '✨ API Credentials (api_key, api_secret, client_id, client_secret) werden automatisch generiert!'
                }),
                ('⚙️ Einstellungen', {
                    'fields': ('is_active', 'auto_register_users', 'require_email_verification')
                }),
                ('📝 Pflichtfelder bei Registrierung', {
                    'fields': ('require_first_name', 'require_last_name', 'require_phone',
                              'require_address', 'require_date_of_birth', 'require_company'),
                    'description': 'Wähle, welche Felder bei der Registrierung auf dieser Website erforderlich sind'
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
        # UserRole hat related_name='user_role_assignments', nicht 'roles'
        count = obj.user_role_assignments.count()
        if count > 0:
            return f"🎭 {count}"
        return "—"
    get_roles_count.short_description = 'Rollenzuweisungen'
    
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


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    """Admin interface for API Request Logs"""
    list_display = (
        'timestamp_display',
        'method',
        'path_short',
        'status_code',
        'user_email',
        'ip_address',
        'duration_ms',
        'is_error_display'
    )
    list_filter = (
        'method',
        'status_code',
        'user',
    )
    search_fields = (
        'path',
        'ip_address',
        'user__email',
        'user__username',
        'request_body',
        'response_body'
    )
    readonly_fields = (
        'id',
        'user',
        'method',
        'path',
        'query_params',
        'request_body',
        'response_body',
        'status_code',
        'ip_address',
        'user_agent',
        'headers',
        'referer',
        'duration',
        'timestamp',
        'formatted_request',
        'formatted_response',
        'formatted_headers',
        'get_duration_ms_display',
    )
    date_hierarchy = None
    ordering = ('-timestamp',)
    list_per_page = 50
    
    fieldsets = (
        ('📊 Übersicht', {
            'fields': ('id', 'timestamp', 'duration', 'get_duration_ms_display', 'status_code')
        }),
        ('🔗 Request', {
            'fields': ('method', 'path', 'query_params', 'user', 'ip_address', 'user_agent', 'referer')
        }),
        ('📝 Request Details', {
            'fields': ('formatted_request', 'request_body'),
            'classes': ('collapse',)
        }),
        ('📤 Response Details', {
            'fields': ('formatted_response', 'response_body'),
            'classes': ('collapse',)
        }),
        ('🔧 Headers', {
            'fields': ('formatted_headers', 'headers'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Logs cannot be manually added"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs cannot be edited"""
        return False
    
    def path_short(self, obj):
        """Shortened path for list view"""
        if not obj or not obj.path:
            return '-'
        if len(obj.path) > 50:
            return f"{obj.path[:47]}..."
        return obj.path
    path_short.short_description = 'Pfad'
    
    def timestamp_display(self, obj):
        """Format timestamp for display"""
        if not obj or not obj.timestamp:
            return '-'
        from django.utils import timezone
        local_time = timezone.localtime(obj.timestamp)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Zeit'
    timestamp_display.admin_order_field = 'timestamp'
    
    def user_email(self, obj):
        """User email or Anonymous"""
        if obj and obj.user:
            return obj.user.email
        return 'Anonymous'
    user_email.short_description = 'Benutzer'
    
    def get_duration_ms_display(self, obj):
        """Duration in milliseconds for detail view"""
        if obj and obj.duration:
            return f"{round(obj.duration * 1000, 2)} ms"
        return '-'
    get_duration_ms_display.short_description = 'Dauer (ms)'
    
    def duration_ms(self, obj):
        """Duration in milliseconds"""
        if not obj:
            return '-'
        ms = obj.get_duration_ms()
        if ms:
            if ms < 100:
                color = 'green'
            elif ms < 500:
                color = 'orange'
            else:
                color = 'red'
            return format_html('<span style="color: {};">{} ms</span>', color, ms)
        return '-'
    duration_ms.short_description = 'Dauer'
    
    def is_error_display(self, obj):
        """Visual indicator for errors"""
        if not obj:
            return '⚠️'
        if obj.is_error():
            return '❌'
        elif obj.is_success():
            return '✅'
        return '⚠️'
    is_error_display.short_description = 'Status'
    
    def formatted_request(self, obj):
        """Pretty formatted request body"""
        if not obj or not obj.request_body:
            return '-'
        
        try:
            import json
            data = json.loads(obj.request_body)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', formatted)
        except:
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', obj.request_body)
    formatted_request.short_description = 'Request Body (formatiert)'
    
    def formatted_response(self, obj):
        """Pretty formatted response body"""
        if not obj or not obj.response_body:
            return '-'
        
        try:
            import json
            data = json.loads(obj.response_body)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', formatted)
        except:
            body = obj.response_body[:1000] if obj.response_body else ''
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', body)
    formatted_response.short_description = 'Response Body (formatiert)'
    
    def formatted_headers(self, obj):
        """Pretty  or not objformatted headers"""
        if not obj.headers:
            return '-'
        
        try:
            import json
            data = json.loads(obj.headers)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>', formatted)
        except:
            return obj.headers
    formatted_headers.short_description = 'Headers (formatiert)'
