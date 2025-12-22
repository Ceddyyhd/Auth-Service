"""
Script zum Generieren von API Keys für existierende Websites
"""
import os
import sys
import django

# Django Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()

from accounts.models import Website
import secrets

def generate_api_keys():
    """Generiert API Keys für alle Websites ohne Keys"""
    websites = Website.objects.all()
    
    if not websites.exists():
        print("❌ Keine Websites gefunden.")
        return
    
    print(f"📊 {websites.count()} Website(s) gefunden\n")
    
    for website in websites:
        updated = False
        
        # API Key generieren falls nicht vorhanden
        if not website.api_key:
            website.api_key = f"pk_{secrets.token_urlsafe(32)}"
            updated = True
            print(f"✅ API Key generiert für: {website.name}")
        
        # API Secret generieren falls nicht vorhanden
        if not website.api_secret:
            website.api_secret = f"sk_{secrets.token_urlsafe(32)}"
            updated = True
            print(f"✅ API Secret generiert für: {website.name}")
        
        if updated:
            website.save()
            print(f"\n📋 Credentials für {website.name}:")
            print(f"   Website ID:  {website.id}")
            print(f"   API Key:     {website.api_key}")
            print(f"   API Secret:  {website.api_secret}")
            print(f"   Client ID:   {website.client_id}")
            print(f"   Client Secret: {website.client_secret}")
            print("-" * 70)
        else:
            print(f"ℹ️  {website.name} hat bereits API Keys")
    
    print("\n✅ Fertig! Alle Websites haben jetzt API Keys.")
    print("⚠️  WICHTIG: Kopiere die API Secrets jetzt, sie werden später verschleiert!")

if __name__ == '__main__':
    generate_api_keys()
