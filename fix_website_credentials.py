#!/usr/bin/env python
"""
Script to fix existing websites that don't have client_id/client_secret.
Run this after migration 0008.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()

from accounts.models import Website

def fix_websites():
    """Generate missing client_id and client_secret for existing websites."""
    websites = Website.objects.all()
    fixed_count = 0
    
    for website in websites:
        needs_update = False
        
        if not website.client_id:
            print(f"⚠️  {website.name} fehlt client_id - wird generiert...")
            needs_update = True
        
        if not website.client_secret:
            print(f"⚠️  {website.name} fehlt client_secret - wird generiert...")
            needs_update = True
        
        if needs_update:
            website.save()  # save() generiert automatisch fehlende Credentials
            print(f"✅ {website.name} aktualisiert")
            print(f"   client_id: {website.client_id}")
            print(f"   client_secret: {website.client_secret[:20]}...")
            fixed_count += 1
    
    if fixed_count == 0:
        print("✅ Alle Websites haben bereits client_id und client_secret")
    else:
        print(f"\n✅ {fixed_count} Website(s) wurden aktualisiert")

if __name__ == '__main__':
    print("🔧 Überprüfe Websites auf fehlende Credentials...\n")
    fix_websites()
