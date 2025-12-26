"""
Django Management Command zum Synchronisieren von Benutzern mit Lexware.
Erstellt fehlende Kontakte und aktualisiert bestehende.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from accounts.models import User
from accounts.lexware_integration import get_lexware_client, LexwareAPIError


class Command(BaseCommand):
    help = 'Synchronisiert Benutzer mit Lexware (erstellt/aktualisiert Kontakte)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Erstellt Lexware-Kontakte für Benutzer die noch keinen haben',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Aktualisiert bestehende Lexware-Kontakte',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Zeigt nur an was getan würde, ohne Änderungen vorzunehmen',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Synchronisiert nur einen bestimmten Benutzer (nach E-Mail)',
        )

    def handle(self, *args, **options):
        # Prüfe ob Lexware API Key konfiguriert ist
        if not getattr(settings, 'LEXWARE_API_KEY', None):
            raise CommandError(
                'LEXWARE_API_KEY ist nicht in den Settings konfiguriert. '
                'Bitte füge den API Key zur .env Datei hinzu.'
            )
        
        dry_run = options['dry_run']
        create_missing = options['create_missing']
        update_existing = options['update_existing']
        specific_email = options.get('email')
        
        if not create_missing and not update_existing:
            self.stdout.write(
                self.style.WARNING(
                    'Keine Aktion ausgewählt. Bitte --create-missing und/oder --update-existing angeben.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - Keine Änderungen werden vorgenommen'))
        
        lexware = get_lexware_client()
        
        # Wähle Benutzer aus
        if specific_email:
            users = User.objects.filter(email=specific_email)
            if not users.exists():
                raise CommandError(f'Benutzer mit E-Mail "{specific_email}" nicht gefunden.')
        else:
            users = User.objects.filter(is_active=True)
        
        total_users = users.count()
        created_count = 0
        updated_count = 0
        error_count = 0
        skipped_count = 0
        
        self.stdout.write(f'\nSynchronisiere {total_users} Benutzer mit Lexware...\n')
        self.stdout.write('⏱️  Rate Limit: 2 Anfragen/Sekunde - Dies kann etwas dauern...\n')
        
        for user in users:
            user_info = f"{user.email} (ID: {user.id})"
            
            # Erstelle fehlende Kontakte
            if create_missing and not user.lexware_contact_id:
                # Validiere Daten vor Erstellung
                is_valid, error_msg = lexware.validate_user_data(user)
                
                if not is_valid:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⊘ Übersprungen: {user_info} - {error_msg}'
                        )
                    )
                    skipped_count += 1
                    continue
                
                try:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'[DRY RUN] Würde Lexware-Kontakt erstellen für: {user_info}'
                            )
                        )
                        created_count += 1
                    else:
                        contact = lexware.create_customer_contact(user)
                        customer_number = contact.get('roles', {}).get('customer', {}).get('number')
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Kontakt erstellt für {user_info} - '
                                f'Kundennummer: {customer_number}'
                            )
                        )
                        created_count += 1
                except LexwareAPIError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Fehler beim Erstellen für {user_info}: {str(e)}'
                        )
                    )
                    error_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Unerwarteter Fehler für {user_info}: {str(e)}'
                        )
                    )
                    error_count += 1
            
            # Aktualisiere bestehende Kontakte
            elif update_existing and user.lexware_contact_id:
                try:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'[DRY RUN] Würde Lexware-Kontakt aktualisieren für: {user_info} '
                                f'(Lexware-ID: {user.lexware_contact_id})'
                            )
                        )
                        updated_count += 1
                    else:
                        lexware.update_customer_contact(user)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Kontakt aktualisiert für {user_info} - '
                                f'Kundennummer: {user.lexware_customer_number}'
                            )
                        )
                        updated_count += 1
                except LexwareAPIError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Fehler beim Aktualisieren für {user_info}: {str(e)}'
                        )
                    )
                    error_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Unerwarteter Fehler für {user_info}: {str(e)}'
                        )
                    )
                    error_count += 1
            else:
                skipped_count += 1
        
        # Zusammenfassung
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('\nSynchronisation abgeschlossen!\n'))
        self.stdout.write(f'Gesamt:        {total_users}')
        self.stdout.write(f'Erstellt:      {created_count}')
        self.stdout.write(f'Aktualisiert:  {updated_count}')
        self.stdout.write(f'Übersprungen:  {skipped_count}')
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Fehler:        {error_count}'))
        else:
            self.stdout.write(f'Fehler:        {error_count}')
        
        self.stdout.write('=' * 60 + '\n')
