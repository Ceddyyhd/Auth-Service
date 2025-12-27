#!/usr/bin/env python
"""
Script zum Anzeigen aller API-Keys aus der Datenbank.
Nützlich für Testing und Entwicklung.

Usage:
    python show_api_keys.py
"""
import os
import sys
import django

# Django Setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()

from accounts.models import Website


def main():
    """Zeige alle API-Keys aus der Datenbank."""
    print("=" * 80)
    print("API-KEYS FÜR AUTH-SERVICE")
    print("=" * 80)
    print()
    
    websites = Website.objects.all()
    
    if not websites:
        print("⚠️  Keine Websites in der Datenbank gefunden!")
        print()
        print("Erstellen Sie zuerst eine Website:")
        print("1. Django Admin öffnen: http://localhost:8000/admin/")
        print("2. Zu 'Accounts > Websites' navigieren")
        print("3. Neue Website erstellen")
        print()
        print("Oder verwenden Sie:")
        print("  python manage.py shell")
        print("  >>> from accounts.models import Website")
        print("  >>> Website.objects.create(name='Test', domain='test.com', callback_url='http://test.com/callback')")
        return
    
    print(f"Gefundene Websites: {websites.count()}")
    print()
    
    for i, website in enumerate(websites, 1):
        print(f"Website #{i}")
        print("-" * 80)
        print(f"Name:         {website.name}")
        print(f"Domain:       {website.domain}")
        print(f"Aktiv:        {'✅ Ja' if website.is_active else '❌ Nein'}")
        print(f"Callback URL: {website.callback_url}")
        print()
        print(f"🔑 API-Key:    {website.api_key}")
        print(f"🔐 API-Secret: {website.api_secret}")
        print()
        print(f"Client ID:     {website.client_id}")
        print(f"Client Secret: {website.client_secret}")
        print()
        
        # Zeige Beispiel-Verwendung
        print("Beispiel-Request (cURL):")
        print(f'curl -X POST http://localhost:8000/api/accounts/login/ \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -H "X-API-Key: {website.api_key}" \\')
        print(f'  -d \'{{"username": "user@example.com", "password": "pass"}}\'')
        print()
        
        print("Beispiel-Request (JavaScript):")
        print("fetch('http://localhost:8000/api/accounts/login/', {")
        print("  method: 'POST',")
        print("  headers: {")
        print("    'Content-Type': 'application/json',")
        print(f"    'X-API-Key': '{website.api_key}'")
        print("  },")
        print("  body: JSON.stringify({")
        print("    username: 'user@example.com',")
        print("    password: 'password123'")
        print("  })")
        print("})")
        print()
        
        print("Beispiel-Request (Python):")
        print("import requests")
        print()
        print(f"headers = {{'X-API-Key': '{website.api_key}'}}")
        print("data = {'username': 'user@example.com', 'password': 'pass'}")
        print("response = requests.post(")
        print("    'http://localhost:8000/api/accounts/login/',")
        print("    json=data,")
        print("    headers=headers")
        print(")")
        print()
        
        if i < websites.count():
            print("=" * 80)
            print()
    
    print()
    print("💡 SICHERHEITSHINWEISE:")
    print("-" * 80)
    print("1. API-Keys NIEMALS in öffentlichen Repositories speichern")
    print("2. Verwenden Sie Umgebungsvariablen für API-Keys")
    print("3. Übertragen Sie API-Keys nur über HTTPS")
    print("4. Rotieren Sie API-Keys regelmäßig")
    print("=" * 80)


if __name__ == '__main__':
    main()
