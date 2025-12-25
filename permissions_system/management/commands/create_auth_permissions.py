"""
Management command to create all Auth Service permissions
"""
from django.core.management.base import BaseCommand
from permissions_system.models import Permission
from accounts.models import Website
import secrets


class Command(BaseCommand):
    help = 'Erstellt alle Auth-Service Berechtigungen für auth.palmdynamicx.de'

    def handle(self, *args, **options):
        # Get or create auth.palmdynamicx.de website
        auth_website, created = Website.objects.get_or_create(
            domain='auth.palmdynamicx.de',
            defaults={
                'name': 'Auth Service',
                'callback_url': 'https://auth.palmdynamicx.de/callback',
                'client_id': 'auth-service-palmdynamicx',
                'client_secret': secrets.token_urlsafe(32),
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Website erstellt: {auth_website.name} ({auth_website.domain})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'ℹ️  Website gefunden: {auth_website.name} ({auth_website.domain})')
            )
        permissions = [
            # Authentication & User Management
            {
                'codename': 'auth.register_user',
                'name': 'Benutzer registrieren',
                'description': 'Erlaubt die Registrierung neuer Benutzer',
                'scope': 'local',
                'category': 'Authentifizierung'
            },
            {
                'codename': 'auth.login_user',
                'name': 'Benutzer anmelden',
                'description': 'Erlaubt die Anmeldung von Benutzern',
                'scope': 'local',
                'category': 'Authentifizierung'
            },
            {
                'codename': 'auth.logout_user',
                'name': 'Benutzer abmelden',
                'description': 'Erlaubt die Abmeldung von Benutzern',
                'scope': 'local',
                'category': 'Authentifizierung'
            },
            {
                'codename': 'auth.refresh_token',
                'name': 'Token erneuern',
                'description': 'Erlaubt die Erneuerung von Access Tokens',
                'scope': 'local',
                'category': 'Authentifizierung'
            },
            
            # Profile Management
            {
                'codename': 'profile.view_own',
                'name': 'Eigenes Profil ansehen',
                'description': 'Erlaubt das Ansehen des eigenen Benutzerprofils',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            {
                'codename': 'profile.edit_own',
                'name': 'Eigenes Profil bearbeiten',
                'description': 'Erlaubt die Bearbeitung des eigenen Profils',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            {
                'codename': 'profile.view_all',
                'name': 'Alle Profile ansehen',
                'description': 'Erlaubt das Ansehen aller Benutzerprofile',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            {
                'codename': 'profile.edit_all',
                'name': 'Alle Profile bearbeiten',
                'description': 'Erlaubt die Bearbeitung aller Benutzerprofile',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            {
                'codename': 'profile.delete',
                'name': 'Profile löschen',
                'description': 'Erlaubt das Löschen von Benutzerprofilen',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            {
                'codename': 'profile.change_password',
                'name': 'Passwort ändern',
                'description': 'Erlaubt die Änderung des eigenen Passworts',
                'scope': 'local',
                'category': 'Profilverwaltung'
            },
            
            # Email Management
            {
                'codename': 'email.verify',
                'name': 'E-Mail verifizieren',
                'description': 'Erlaubt die Verifizierung von E-Mail-Adressen',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            {
                'codename': 'email.resend_verification',
                'name': 'Verifizierungs-E-Mail erneut senden',
                'description': 'Erlaubt das erneute Senden von Verifizierungs-E-Mails',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            {
                'codename': 'email.request_password_reset',
                'name': 'Passwort-Reset anfordern',
                'description': 'Erlaubt die Anforderung eines Passwort-Resets',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            {
                'codename': 'email.reset_password',
                'name': 'Passwort zurücksetzen',
                'description': 'Erlaubt das Zurücksetzen des Passworts',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            {
                'codename': 'email.test_smtp',
                'name': 'SMTP testen',
                'description': 'Erlaubt das Testen der SMTP-Konfiguration',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            {
                'codename': 'email.view_smtp_config',
                'name': 'SMTP-Konfiguration ansehen',
                'description': 'Erlaubt das Ansehen der SMTP-Konfiguration',
                'scope': 'local',
                'category': 'E-Mail-Verwaltung'
            },
            
            # MFA Management
            {
                'codename': 'mfa.enable',
                'name': 'MFA aktivieren',
                'description': 'Erlaubt die Aktivierung der Zwei-Faktor-Authentifizierung',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            {
                'codename': 'mfa.disable',
                'name': 'MFA deaktivieren',
                'description': 'Erlaubt die Deaktivierung der Zwei-Faktor-Authentifizierung',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            {
                'codename': 'mfa.verify_setup',
                'name': 'MFA-Einrichtung verifizieren',
                'description': 'Erlaubt die Verifizierung der MFA-Einrichtung',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            {
                'codename': 'mfa.regenerate_backup_codes',
                'name': 'Backup-Codes neu generieren',
                'description': 'Erlaubt die Neugenerierung von MFA-Backup-Codes',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            {
                'codename': 'mfa.view_status',
                'name': 'MFA-Status ansehen',
                'description': 'Erlaubt das Ansehen des MFA-Status',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            {
                'codename': 'mfa.verify_token',
                'name': 'MFA-Token verifizieren',
                'description': 'Erlaubt die Verifizierung von MFA-Tokens',
                'scope': 'local',
                'category': 'MFA-Verwaltung'
            },
            
            # SSO Management
            {
                'codename': 'sso.initiate',
                'name': 'SSO initiieren',
                'description': 'Erlaubt die Initiierung von Single Sign-On',
                'scope': 'local',
                'category': 'SSO-Verwaltung'
            },
            {
                'codename': 'sso.exchange_token',
                'name': 'SSO-Token tauschen',
                'description': 'Erlaubt den Austausch von SSO-Tokens',
                'scope': 'local',
                'category': 'SSO-Verwaltung'
            },
            {
                'codename': 'sso.check_status',
                'name': 'SSO-Status prüfen',
                'description': 'Erlaubt das Prüfen des SSO-Status',
                'scope': 'local',
                'category': 'SSO-Verwaltung'
            },
            {
                'codename': 'sso.logout',
                'name': 'SSO-Abmeldung',
                'description': 'Erlaubt die Abmeldung vom SSO',
                'scope': 'local',
                'category': 'SSO-Verwaltung'
            },
            
            # Social Login
            {
                'codename': 'social.login',
                'name': 'Social Login',
                'description': 'Erlaubt die Anmeldung über Social Media (Google, etc.)',
                'scope': 'local',
                'category': 'Social Login'
            },
            {
                'codename': 'social.complete_profile',
                'name': 'Profil vervollständigen',
                'description': 'Erlaubt das Vervollständigen des Profils nach Social Login',
                'scope': 'local',
                'category': 'Social Login'
            },
            {
                'codename': 'social.view_accounts',
                'name': 'Verknüpfte Konten ansehen',
                'description': 'Erlaubt das Ansehen verknüpfter Social-Media-Konten',
                'scope': 'local',
                'category': 'Social Login'
            },
            {
                'codename': 'social.unlink_account',
                'name': 'Konto trennen',
                'description': 'Erlaubt das Trennen von Social-Media-Konten',
                'scope': 'local',
                'category': 'Social Login'
            },
            
            # Website Management
            {
                'codename': 'website.create',
                'name': 'Website erstellen',
                'description': 'Erlaubt das Erstellen neuer Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.view_own',
                'name': 'Eigene Websites ansehen',
                'description': 'Erlaubt das Ansehen eigener Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.view_all',
                'name': 'Alle Websites ansehen',
                'description': 'Erlaubt das Ansehen aller Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.edit_own',
                'name': 'Eigene Websites bearbeiten',
                'description': 'Erlaubt die Bearbeitung eigener Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.edit_all',
                'name': 'Alle Websites bearbeiten',
                'description': 'Erlaubt die Bearbeitung aller Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.delete_own',
                'name': 'Eigene Websites löschen',
                'description': 'Erlaubt das Löschen eigener Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.delete_all',
                'name': 'Alle Websites löschen',
                'description': 'Erlaubt das Löschen aller Websites',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.manage_api_keys',
                'name': 'API-Keys verwalten',
                'description': 'Erlaubt die Verwaltung von Website API-Keys',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            {
                'codename': 'website.view_required_fields',
                'name': 'Pflichtfelder ansehen',
                'description': 'Erlaubt das Ansehen der Website-Pflichtfelder',
                'scope': 'local',
                'category': 'Website-Verwaltung'
            },
            
            # Access Control
            {
                'codename': 'access.verify',
                'name': 'Zugriff verifizieren',
                'description': 'Erlaubt die Verifizierung von Website-Zugriffen',
                'scope': 'local',
                'category': 'Zugriffskontrolle'
            },
            {
                'codename': 'access.grant',
                'name': 'Zugriff gewähren',
                'description': 'Erlaubt das Gewähren von Website-Zugriffen',
                'scope': 'local',
                'category': 'Zugriffskontrolle'
            },
            {
                'codename': 'access.revoke',
                'name': 'Zugriff entziehen',
                'description': 'Erlaubt das Entziehen von Website-Zugriffen',
                'scope': 'local',
                'category': 'Zugriffskontrolle'
            },
            
            # Session Management
            {
                'codename': 'session.view_own',
                'name': 'Eigene Sitzungen ansehen',
                'description': 'Erlaubt das Ansehen eigener aktiver Sitzungen',
                'scope': 'local',
                'category': 'Sitzungsverwaltung'
            },
            {
                'codename': 'session.view_all',
                'name': 'Alle Sitzungen ansehen',
                'description': 'Erlaubt das Ansehen aller Benutzersitzungen',
                'scope': 'local',
                'category': 'Sitzungsverwaltung'
            },
            {
                'codename': 'session.terminate_own',
                'name': 'Eigene Sitzungen beenden',
                'description': 'Erlaubt das Beenden eigener Sitzungen',
                'scope': 'local',
                'category': 'Sitzungsverwaltung'
            },
            {
                'codename': 'session.terminate_all',
                'name': 'Alle Sitzungen beenden',
                'description': 'Erlaubt das Beenden aller Benutzersitzungen',
                'scope': 'local',
                'category': 'Sitzungsverwaltung'
            },
            
            # Permission Management
            {
                'codename': 'permission.create',
                'name': 'Berechtigungen erstellen',
                'description': 'Erlaubt das Erstellen neuer Berechtigungen',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            {
                'codename': 'permission.view',
                'name': 'Berechtigungen ansehen',
                'description': 'Erlaubt das Ansehen von Berechtigungen',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            {
                'codename': 'permission.edit',
                'name': 'Berechtigungen bearbeiten',
                'description': 'Erlaubt die Bearbeitung von Berechtigungen',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            {
                'codename': 'permission.delete',
                'name': 'Berechtigungen löschen',
                'description': 'Erlaubt das Löschen von Berechtigungen',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            {
                'codename': 'permission.assign',
                'name': 'Berechtigungen zuweisen',
                'description': 'Erlaubt das Zuweisen von Berechtigungen an Benutzer',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            {
                'codename': 'permission.check',
                'name': 'Berechtigungen prüfen',
                'description': 'Erlaubt das Prüfen von Benutzerberechtigungen',
                'scope': 'local',
                'category': 'Berechtigungsverwaltung'
            },
            
            # Role Management
            {
                'codename': 'role.create',
                'name': 'Rollen erstellen',
                'description': 'Erlaubt das Erstellen neuer Rollen',
                'scope': 'local',
                'category': 'Rollenverwaltung'
            },
            {
                'codename': 'role.view',
                'name': 'Rollen ansehen',
                'description': 'Erlaubt das Ansehen von Rollen',
                'scope': 'local',
                'category': 'Rollenverwaltung'
            },
            {
                'codename': 'role.edit',
                'name': 'Rollen bearbeiten',
                'description': 'Erlaubt die Bearbeitung von Rollen',
                'scope': 'local',
                'category': 'Rollenverwaltung'
            },
            {
                'codename': 'role.delete',
                'name': 'Rollen löschen',
                'description': 'Erlaubt das Löschen von Rollen',
                'scope': 'local',
                'category': 'Rollenverwaltung'
            },
            {
                'codename': 'role.assign',
                'name': 'Rollen zuweisen',
                'description': 'Erlaubt das Zuweisen von Rollen an Benutzer',
                'scope': 'local',
                'category': 'Rollenverwaltung'
            },
            {
                'codename': 'role.assign_permissions',
                'name': 'Berechtigungen zu Rollen zuweisen',
                'description': 'Erlaubt das Zuweisen von Berechtigungen zu Rollen',
                'scope': 'local',
                'category': 'Rollenverwaltung'
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
                    'website': auth_website,  # Link to auth.palmdynamicx.de
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
            self.style.SUCCESS(
                f'\n✨ Fertig! {created_count} erstellt, {updated_count} aktualisiert'
            )
        )
