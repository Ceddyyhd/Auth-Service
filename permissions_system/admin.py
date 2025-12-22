from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Permission, Role, UserRole, UserPermission


# Verstecke Django's verwirrende Groups - wir nutzen unser eigenes System
admin.site.unregister(Group)


class RolePermissionInline(admin.TabularInline):
    """Inline für Berechtigungen in einer Rolle"""
    model = Role.permissions.through
    extra = 1
    verbose_name = 'Berechtigung'
    verbose_name_plural = '🔑 Berechtigungen dieser Rolle'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Berechtigungen definieren - Basis-Bausteine des Systems
    """
    list_display = ('name', 'codename', 'get_scope_display', 'get_website_display', 'created_at')
    list_filter = ('scope', 'website', 'created_at')
    search_fields = ('name', 'codename', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('📋 Grundinformationen', {
            'fields': ('name', 'codename', 'description'),
            'description': 'Definiere eine neue Berechtigung (z.B. "Berichte ansehen", "Benutzer bearbeiten")'
        }),
        ('🌍 Geltungsbereich', {
            'fields': ('scope', 'website'),
            'description': (
                '<strong>Global:</strong> Gilt für alle Websites<br>'
                '<strong>Lokal:</strong> Gilt nur für eine spezifische Website (Website auswählen erforderlich)'
            )
        }),
        ('📅 Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_scope_display(self, obj):
        if obj.scope == 'global':
            return '🌍 Global'
        return '🏠 Lokal'
    get_scope_display.short_description = 'Bereich'
    
    def get_website_display(self, obj):
        if obj.website:
            return f"🌐 {obj.website.name}"
        return "—"
    get_website_display.short_description = 'Website'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Rollen gruppieren mehrere Berechtigungen
    """
    list_display = ('name', 'get_scope_display', 'get_website_display', 
                    'get_permissions_count', 'get_users_count', 'created_at')
    list_filter = ('scope', 'website', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('📋 Grundinformationen', {
            'fields': ('name', 'description'),
            'description': 'Erstelle eine Rolle die mehrere Berechtigungen bündelt (z.B. "Editor", "Administrator")'
        }),
        ('🌍 Geltungsbereich', {
            'fields': ('scope', 'website'),
            'description': (
                '<strong>Global:</strong> Kann allen Benutzern zugewiesen werden<br>'
                '<strong>Lokal:</strong> Nur für Benutzer einer spezifischen Website'
            )
        }),
        ('🔑 Berechtigungen', {
            'fields': ('permissions',),
            'description': 'Wähle alle Berechtigungen, die diese Rolle haben soll'
        }),
        ('📅 Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_scope_display(self, obj):
        if obj.scope == 'global':
            return '🌍 Global'
        return '🏠 Lokal'
    get_scope_display.short_description = 'Bereich'
    
    def get_website_display(self, obj):
        if obj.website:
            return f"🌐 {obj.website.name}"
        return "—"
    get_website_display.short_description = 'Website'
    
    def get_permissions_count(self, obj):
        count = obj.permissions.count()
        return f"🔑 {count} Berechtigung(en)"
    get_permissions_count.short_description = 'Berechtigungen'
    
    def get_users_count(self, obj):
        count = obj.user_assignments.count()
        if count > 0:
            return f"👥 {count} Benutzer"
        return "—"
    get_users_count.short_description = 'Zugewiesen an'


# UserRole und UserPermission werden NICHT mehr separat registriert
# Diese werden nur noch über das User-Profil verwaltet (siehe accounts/admin.py)

# Info-Text für die Admin-Oberfläche
admin.site.site_header = '🔐 Auth Service Administration'
admin.site.site_title = 'Auth Service'
admin.site.index_title = 'Willkommen im Auth Service Admin'
