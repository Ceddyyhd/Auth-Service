"""
Management command to create Django Admin permissions
These map custom permissions to Django's built-in admin permissions.
"""
from django.core.management.base import BaseCommand
from permissions_system.models import Permission
from accounts.models import Website
import secrets


class Command(BaseCommand):
    help = 'Erstellt Django Admin Berechtigungen für einheitliches System'

    def handle(self, *args, **options):
        # Get or create auth.palmdynamicx.de website
        auth_website = Website.objects.filter(domain='auth.palmdynamicx.de').first()
        
        if not auth_website:
            self.stdout.write(
                self.style.ERROR('❌ auth.palmdynamicx.de Website nicht gefunden. Führe erst create_auth_permissions aus.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Website gefunden: {auth_website.name} ({auth_website.domain})')
        )
        
        # Django Admin Permissions (für Staff-Zugriff auf verschiedene Models)
        permissions = [
            # User Management
            {
                'codename': 'accounts.view_user',
                'name': 'Benutzer ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Benutzern im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.add_user',
                'name': 'Benutzer hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Benutzern im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.change_user',
                'name': 'Benutzer bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Benutzern im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.delete_user',
                'name': 'Benutzer löschen (Admin)',
                'description': 'Erlaubt das Löschen von Benutzern im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            
            # Website Management
            {
                'codename': 'accounts.view_website',
                'name': 'Websites ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Websites im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.add_website',
                'name': 'Websites hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Websites im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.change_website',
                'name': 'Websites bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Websites im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'accounts.delete_website',
                'name': 'Websites löschen (Admin)',
                'description': 'Erlaubt das Löschen von Websites im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            
            # Permission Management
            {
                'codename': 'permissions_system.view_permission',
                'name': 'Berechtigungen ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Berechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.add_permission',
                'name': 'Berechtigungen hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Berechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.change_permission',
                'name': 'Berechtigungen bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Berechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.delete_permission',
                'name': 'Berechtigungen löschen (Admin)',
                'description': 'Erlaubt das Löschen von Berechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            
            # Role Management
            {
                'codename': 'permissions_system.view_role',
                'name': 'Rollen ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Rollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.add_role',
                'name': 'Rollen hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Rollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.change_role',
                'name': 'Rollen bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Rollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.delete_role',
                'name': 'Rollen löschen (Admin)',
                'description': 'Erlaubt das Löschen von Rollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            
            # User Role Management
            {
                'codename': 'permissions_system.view_userrole',
                'name': 'Benutzerrollen ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Benutzerrollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.add_userrole',
                'name': 'Benutzerrollen hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Benutzerrollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.change_userrole',
                'name': 'Benutzerrollen bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Benutzerrollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.delete_userrole',
                'name': 'Benutzerrollen löschen (Admin)',
                'description': 'Erlaubt das Löschen von Benutzerrollen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            
            # User Permission Management
            {
                'codename': 'permissions_system.view_userpermission',
                'name': 'Benutzerberechtigungen ansehen (Admin)',
                'description': 'Erlaubt das Ansehen von Benutzerberechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.add_userpermission',
                'name': 'Benutzerberechtigungen hinzufügen (Admin)',
                'description': 'Erlaubt das Hinzufügen von Benutzerberechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.change_userpermission',
                'name': 'Benutzerberechtigungen bearbeiten (Admin)',
                'description': 'Erlaubt die Bearbeitung von Benutzerberechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
            {
                'codename': 'permissions_system.delete_userpermission',
                'name': 'Benutzerberechtigungen löschen (Admin)',
                'description': 'Erlaubt das Löschen von Benutzerberechtigungen im Django Admin',
                'scope': 'local',
                'category': 'Django Admin'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for perm_data in permissions:
            perm, created = Permission.objects.update_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description'],
                    'scope': perm_data['scope'],
                    'website': auth_website,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Berechtigung erstellt: {perm.name} ({perm.codename})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Berechtigung aktualisiert: {perm.name} ({perm.codename})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✨ Fertig! {created_count} erstellt, {updated_count} aktualisiert')
        )
