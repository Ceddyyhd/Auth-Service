"""
Lexware API Integration für Auth-Service
Erstellt automatisch Kundenkontakte in Lexware bei der Benutzerregistrierung.
"""

import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LexwareAPIError(Exception):
    """Custom exception for Lexware API errors"""
    pass


class LexwareIntegration:
    """
    Integration mit der Lexware API.
    Dokumentation: https://developers.lexware.io/docs/
    """
    
    BASE_URL = "https://api.lexware.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert die Lexware API Integration.
        
        Args:
            api_key: Lexware API Key. Falls nicht angegeben, wird aus Settings gelesen.
        """
        self.api_key = api_key or getattr(settings, 'LEXWARE_API_KEY', None)
        if not self.api_key:
            logger.warning("Lexware API Key nicht konfiguriert!")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Führt einen API-Request aus.
        
        Args:
            method: HTTP Methode (GET, POST, PUT, DELETE)
            endpoint: API Endpoint (z.B. '/contacts')
            data: Request Body für POST/PUT
            
        Returns:
            API Response als Dictionary
            
        Raises:
            LexwareAPIError: Bei API-Fehlern
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Ungültige HTTP-Methode: {method}")
            
            response.raise_for_status()
            
            # Bei 204 No Content gibt es keinen Response Body
            if response.status_code == 204:
                return {}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Lexware API Fehler ({response.status_code}): {response.text}"
            logger.error(error_msg)
            raise LexwareAPIError(error_msg) from e
        except requests.exceptions.RequestException as e:
            error_msg = f"Lexware API Verbindungsfehler: {str(e)}"
            logger.error(error_msg)
            raise LexwareAPIError(error_msg) from e
    
    def create_customer_contact(self, user) -> Dict[str, Any]:
        """
        Erstellt einen neuen Kundenkontakt in Lexware.
        
        Args:
            user: User-Objekt aus Django
            
        Returns:
            Dictionary mit Kontakt-Daten inkl. ID und Kundennummer
            
        Raises:
            LexwareAPIError: Bei API-Fehlern
        """
        # Prüfe ob Benutzer bereits einen Lexware-Kontakt hat
        if user.lexware_contact_id:
            logger.info(f"Benutzer {user.email} hat bereits einen Lexware-Kontakt")
            return self.get_contact(user.lexware_contact_id)
        
        # Bereite Kontaktdaten vor
        contact_data = {
            "version": 0,
            "roles": {
                "customer": {}  # Leeres Objekt für Kundenrolle
            }
        }
        
        # Unterscheide zwischen Privat- und Firmenkunden
        if user.company:
            # Firmenkunde
            contact_data["company"] = {
                "name": user.company
            }
            
            # Kontaktperson hinzufügen wenn Name vorhanden
            if user.first_name or user.last_name:
                contact_data["company"]["contactPersons"] = [
                    {
                        "firstName": user.first_name or "",
                        "lastName": user.last_name or user.username,
                        "primary": True,
                        "emailAddress": user.email,
                        "phoneNumber": user.phone or ""
                    }
                ]
        else:
            # Privatkunde
            contact_data["person"] = {
                "firstName": user.first_name or "",
                "lastName": user.last_name or user.username
            }
        
        # Adresse hinzufügen wenn vorhanden
        if user.street or user.city or user.postal_code:
            contact_data["addresses"] = {
                "billing": [
                    {
                        "street": f"{user.street} {user.street_number}".strip() or "",
                        "city": user.city or "",
                        "zip": user.postal_code or "",
                        "countryCode": user.country or "DE"  # Standard Deutschland
                    }
                ]
            }
        
        # E-Mail-Adresse hinzufügen
        contact_data["emailAddresses"] = {
            "business": [user.email] if user.company else [],
            "private": [user.email] if not user.company else []
        }
        
        # Telefonnummer hinzufügen wenn vorhanden
        if user.phone:
            contact_data["phoneNumbers"] = {
                "business": [user.phone] if user.company else [],
                "private": [user.phone] if not user.company else []
            }
        
        # Notiz mit Registrierungsdatum
        contact_data["note"] = f"Automatisch erstellt über Auth-Service am {user.date_joined.strftime('%d.%m.%Y')}"
        
        logger.info(f"Erstelle Lexware-Kontakt für Benutzer {user.email}")
        
        try:
            # Erstelle Kontakt in Lexware
            response = self._make_request('POST', '/contacts', contact_data)
            
            # Lexware gibt bei erfolgreicher Erstellung die ID und resourceUri zurück
            contact_id = response.get('id')
            
            if not contact_id:
                raise LexwareAPIError("Keine Kontakt-ID in Lexware-Response erhalten")
            
            # Hole vollständige Kontaktdaten inkl. Kundennummer
            contact_details = self.get_contact(contact_id)
            
            # Aktualisiere User mit Lexware-Daten
            user.lexware_contact_id = contact_id
            if 'roles' in contact_details and 'customer' in contact_details['roles']:
                user.lexware_customer_number = contact_details['roles']['customer'].get('number')
            user.save(update_fields=['lexware_contact_id', 'lexware_customer_number'])
            
            logger.info(
                f"Lexware-Kontakt erstellt: ID={contact_id}, "
                f"Kundennummer={user.lexware_customer_number}"
            )
            
            return contact_details
            
        except LexwareAPIError as e:
            logger.error(f"Fehler beim Erstellen des Lexware-Kontakts: {str(e)}")
            raise
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Ruft einen Kontakt aus Lexware ab.
        
        Args:
            contact_id: UUID des Kontakts in Lexware
            
        Returns:
            Dictionary mit Kontaktdaten
            
        Raises:
            LexwareAPIError: Bei API-Fehlern
        """
        logger.info(f"Rufe Lexware-Kontakt ab: {contact_id}")
        return self._make_request('GET', f'/contacts/{contact_id}')
    
    def update_customer_contact(self, user) -> Dict[str, Any]:
        """
        Aktualisiert einen bestehenden Kundenkontakt in Lexware.
        
        Args:
            user: User-Objekt aus Django
            
        Returns:
            Dictionary mit aktualisierten Kontaktdaten
            
        Raises:
            LexwareAPIError: Bei API-Fehlern oder wenn kein Kontakt existiert
        """
        if not user.lexware_contact_id:
            raise LexwareAPIError(
                f"Benutzer {user.email} hat noch keinen Lexware-Kontakt. "
                "Bitte zuerst create_customer_contact() aufrufen."
            )
        
        # Hole aktuelle Kontaktdaten für Version-Nummer (Optimistic Locking)
        current_contact = self.get_contact(user.lexware_contact_id)
        version = current_contact.get('version', 0)
        
        # Bereite Update-Daten vor (ähnlich wie bei create)
        contact_data = {
            "version": version,
            "roles": current_contact.get('roles', {"customer": {}})
        }
        
        # Aktualisiere Daten basierend auf User-Informationen
        if user.company:
            contact_data["company"] = {
                "name": user.company
            }
            if user.first_name or user.last_name:
                contact_data["company"]["contactPersons"] = [
                    {
                        "firstName": user.first_name or "",
                        "lastName": user.last_name or user.username,
                        "primary": True,
                        "emailAddress": user.email,
                        "phoneNumber": user.phone or ""
                    }
                ]
        else:
            contact_data["person"] = {
                "firstName": user.first_name or "",
                "lastName": user.last_name or user.username
            }
        
        # Adresse aktualisieren
        if user.street or user.city or user.postal_code:
            contact_data["addresses"] = {
                "billing": [
                    {
                        "street": f"{user.street} {user.street_number}".strip() or "",
                        "city": user.city or "",
                        "zip": user.postal_code or "",
                        "countryCode": user.country or "DE"
                    }
                ]
            }
        
        contact_data["emailAddresses"] = {
            "business": [user.email] if user.company else [],
            "private": [user.email] if not user.company else []
        }
        
        if user.phone:
            contact_data["phoneNumbers"] = {
                "business": [user.phone] if user.company else [],
                "private": [user.phone] if not user.company else []
            }
        
        contact_data["note"] = current_contact.get('note', '') + f"\nAktualisiert am {user.updated_at.strftime('%d.%m.%Y')}"
        
        logger.info(f"Aktualisiere Lexware-Kontakt {user.lexware_contact_id} für Benutzer {user.email}")
        
        try:
            # Update in Lexware
            response = self._make_request('PUT', f'/contacts/{user.lexware_contact_id}', contact_data)
            
            # Hole aktualisierte Kontaktdaten
            updated_contact = self.get_contact(user.lexware_contact_id)
            
            logger.info(f"Lexware-Kontakt {user.lexware_contact_id} erfolgreich aktualisiert")
            
            return updated_contact
            
        except LexwareAPIError as e:
            logger.error(f"Fehler beim Aktualisieren des Lexware-Kontakts: {str(e)}")
            raise
    
    def search_contacts_by_email(self, email: str) -> list:
        """
        Sucht Kontakte in Lexware nach E-Mail-Adresse.
        
        Args:
            email: E-Mail-Adresse zum Suchen
            
        Returns:
            Liste von Kontakten
            
        Raises:
            LexwareAPIError: Bei API-Fehlern
        """
        logger.info(f"Suche Lexware-Kontakte mit E-Mail: {email}")
        response = self._make_request('GET', f'/contacts?email={email}')
        return response.get('content', [])
    
    def get_customer_number(self, user) -> Optional[int]:
        """
        Holt die Kundennummer eines Benutzers aus Lexware.
        
        Args:
            user: User-Objekt aus Django
            
        Returns:
            Kundennummer oder None wenn nicht vorhanden
        """
        if not user.lexware_contact_id:
            return None
        
        try:
            contact = self.get_contact(user.lexware_contact_id)
            if 'roles' in contact and 'customer' in contact['roles']:
                return contact['roles']['customer'].get('number')
        except LexwareAPIError:
            logger.error(f"Fehler beim Abrufen der Kundennummer für {user.email}")
        
        return None


# Singleton-Instanz für einfache Verwendung
_lexware_client = None

def get_lexware_client() -> LexwareIntegration:
    """
    Gibt eine Singleton-Instanz des Lexware-Clients zurück.
    """
    global _lexware_client
    if _lexware_client is None:
        _lexware_client = LexwareIntegration()
    return _lexware_client
