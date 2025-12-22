"""
Python Client Library für Auth Service
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime


class AuthServiceClient:
    """
    Client-Bibliothek für die Kommunikation mit dem Auth Service.
    
    Verwendung:
        client = AuthServiceClient('http://localhost:8000')
        client.login('user@example.com', 'password')
        
        # Zugriff prüfen
        has_access = client.verify_access('website-uuid')
        
        # Berechtigung prüfen
        can_edit = client.check_permission('edit_content', 'website-uuid')
    """
    
    def __init__(self, base_url: str = 'http://localhost:8000'):
        """
        Initialisiert den Client.
        
        Args:
            base_url: Basis-URL des Auth Service
        """
        self.base_url = base_url.rstrip('/')
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Gibt die HTTP-Header mit Authorization Token zurück."""
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def register(self, email: str, username: str, password: str, 
                 first_name: str = '', last_name: str = '', 
                 phone: str = '') -> Dict[str, Any]:
        """
        Registriert einen neuen Benutzer.
        
        Args:
            email: E-Mail-Adresse
            username: Benutzername
            password: Passwort
            first_name: Vorname (optional)
            last_name: Nachname (optional)
            phone: Telefonnummer (optional)
        
        Returns:
            Dict mit Benutzerinformationen und Tokens
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/register/',
            json={
                'email': email,
                'username': username,
                'password': password,
                'password2': password,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Tokens speichern
        self.access_token = data['tokens']['access']
        self.refresh_token = data['tokens']['refresh']
        
        return data
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Meldet einen Benutzer an.
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
        
        Returns:
            Dict mit Tokens
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/login/',
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        
        # Tokens speichern
        self.access_token = data['access']
        self.refresh_token = data['refresh']
        
        return data
    
    def logout(self) -> Dict[str, str]:
        """
        Meldet den aktuellen Benutzer ab.
        
        Returns:
            Dict mit Bestätigungsnachricht
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/logout/',
            json={'refresh': self.refresh_token},
            headers=self._get_headers()
        )
        response.raise_for_status()
        
        # Tokens löschen
        self.access_token = None
        self.refresh_token = None
        
        return response.json()
    
    def refresh_access_token(self) -> str:
        """
        Erneuert den Access Token mit dem Refresh Token.
        
        Returns:
            Neuer Access Token
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/token/refresh/',
            json={'refresh': self.refresh_token}
        )
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data['access']
        return self.access_token
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Ruft das Benutzerprofil ab.
        
        Returns:
            Dict mit Profilinformationen
        """
        response = requests.get(
            f'{self.base_url}/api/accounts/profile/',
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_profile(self, **kwargs) -> Dict[str, Any]:
        """
        Aktualisiert das Benutzerprofil.
        
        Args:
            **kwargs: Felder zum Aktualisieren (first_name, last_name, phone, username)
        
        Returns:
            Dict mit aktualisierten Profilinformationen
        """
        response = requests.put(
            f'{self.base_url}/api/accounts/profile/',
            json=kwargs,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def change_password(self, old_password: str, new_password: str) -> Dict[str, str]:
        """
        Ändert das Passwort des Benutzers.
        
        Args:
            old_password: Altes Passwort
            new_password: Neues Passwort
        
        Returns:
            Dict mit Bestätigungsnachricht
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/change-password/',
            json={
                'old_password': old_password,
                'new_password': new_password,
                'new_password2': new_password,
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def verify_access(self, website_id: str) -> Dict[str, Any]:
        """
        Prüft, ob der Benutzer Zugriff auf eine Website hat.
        
        Args:
            website_id: UUID der Website
        
        Returns:
            Dict mit Zugriffsinformationen
        """
        response = requests.post(
            f'{self.base_url}/api/accounts/verify-access/',
            json={'website_id': website_id},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_all_permissions(self, website_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ruft alle Berechtigungen des aktuellen Benutzers ab.
        
        Args:
            website_id: UUID der Website (optional)
        
        Returns:
            Dict mit allen Berechtigungen
        """
        url = f'{self.base_url}/api/permissions/check/me/'
        if website_id:
            url += f'?website_id={website_id}'
        
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def check_permission(self, permission_codename: str, 
                        website_id: Optional[str] = None) -> bool:
        """
        Prüft, ob der Benutzer eine spezifische Berechtigung hat.
        
        Args:
            permission_codename: Codename der Berechtigung
            website_id: UUID der Website (optional)
        
        Returns:
            True wenn Berechtigung vorhanden, sonst False
        """
        data = {'permission_codename': permission_codename}
        if website_id:
            data['website_id'] = website_id
        
        response = requests.post(
            f'{self.base_url}/api/permissions/check-permission/',
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()['has_permission']
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Ruft alle aktiven Sitzungen des Benutzers ab.
        
        Returns:
            Liste von Sitzungen
        """
        response = requests.get(
            f'{self.base_url}/api/accounts/sessions/',
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()['results']


# Beispiel-Verwendung
if __name__ == '__main__':
    # Client initialisieren
    client = AuthServiceClient('http://localhost:8000')
    
    # Registrieren oder Einloggen
    try:
        client.login('user@example.com', 'password123')
        print("✅ Erfolgreich eingeloggt")
    except:
        print("Registrierung erforderlich...")
        client.register(
            email='user@example.com',
            username='testuser',
            password='password123',
            first_name='Max',
            last_name='Mustermann'
        )
        print("✅ Erfolgreich registriert")
    
    # Profil abrufen
    profile = client.get_profile()
    print(f"\n👤 Profil: {profile['email']}")
    
    # Berechtigungen prüfen (Beispiel)
    # has_access = client.verify_access('website-uuid-hier')
    # can_edit = client.check_permission('edit_content', 'website-uuid-hier')
    
    # Alle Berechtigungen abrufen
    permissions = client.get_all_permissions()
    print(f"\n🔐 Globale Berechtigungen: {permissions['global_permissions']}")
    print(f"🔐 Lokale Berechtigungen: {permissions['local_permissions']}")
    
    # Abmelden
    client.logout()
    print("\n✅ Erfolgreich abgemeldet")
