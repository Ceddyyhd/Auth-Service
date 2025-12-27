"""
Custom Permission Classes für API-Key-Authentifizierung
"""
from rest_framework import permissions
from .models import Website


class HasValidAPIKey(permissions.BasePermission):
    """
    Permission-Klasse: Prüft ob ein gültiger API-Key im Request-Header vorhanden ist.
    
    Der API-Key muss im Header 'X-API-Key' übergeben werden.
    Optional kann auch der 'X-API-Secret' Header für zusätzliche Sicherheit geprüft werden.
    
    Verwendung in Views:
        permission_classes = [HasValidAPIKey]
    
    Header-Beispiel:
        X-API-Key: your_api_key_here
        X-API-Secret: your_api_secret_here (optional)
    """
    
    message = 'Ungültiger oder fehlender API-Key. Bitte fügen Sie einen gültigen API-Key im X-API-Key Header hinzu.'
    
    def has_permission(self, request, view):
        # API-Key aus Header holen
        api_key = request.headers.get('X-API-Key') or request.headers.get('X-Api-Key')
        
        if not api_key:
            self.message = 'API-Key fehlt. Bitte fügen Sie den X-API-Key Header zu Ihrer Anfrage hinzu.'
            return False
        
        # Prüfe ob API-Key zu einer aktiven Website gehört
        try:
            website = Website.objects.get(api_key=api_key, is_active=True)
            
            # Optional: Prüfe auch API-Secret falls vorhanden
            api_secret = request.headers.get('X-API-Secret') or request.headers.get('X-Api-Secret')
            if api_secret and website.api_secret and api_secret != website.api_secret:
                self.message = 'API-Secret ist ungültig.'
                return False
            
            # Speichere Website im Request für späteren Zugriff
            request.website = website
            return True
            
        except Website.DoesNotExist:
            self.message = 'API-Key ist ungültig oder die zugehörige Website ist nicht aktiv.'
            return False


class HasValidAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """
    Permission-Klasse: Erlaubt Zugriff mit gültigem API-Key ODER mit JWT-Token.
    
    Nützlich für Endpoints, die sowohl von externen Systemen (mit API-Key)
    als auch von authentifizierten Benutzern (mit JWT-Token) aufgerufen werden können.
    
    Verwendung in Views:
        permission_classes = [HasValidAPIKeyOrIsAuthenticated]
    """
    
    message = 'Authentifizierung erforderlich. Bitte verwenden Sie entweder einen API-Key (X-API-Key Header) oder einen JWT-Token (Authorization Header).'
    
    def has_permission(self, request, view):
        # Prüfe zuerst JWT-Token
        if request.user and request.user.is_authenticated:
            return True
        
        # Falls kein JWT-Token, prüfe API-Key
        api_key = request.headers.get('X-API-Key') or request.headers.get('X-Api-Key')
        
        if not api_key:
            return False
        
        try:
            website = Website.objects.get(api_key=api_key, is_active=True)
            
            # Optional: Prüfe auch API-Secret
            api_secret = request.headers.get('X-API-Secret') or request.headers.get('X-Api-Secret')
            if api_secret and website.api_secret and api_secret != website.api_secret:
                self.message = 'API-Secret ist ungültig.'
                return False
            
            request.website = website
            return True
            
        except Website.DoesNotExist:
            self.message = 'Ungültiger API-Key oder zugehörige Website ist nicht aktiv.'
            return False


class IsAdminOrHasValidAPIKey(permissions.BasePermission):
    """
    Permission-Klasse: Erlaubt Zugriff für Admins ODER mit gültigem API-Key.
    
    Nützlich für administrative Endpoints, die auch programmatisch
    von vertrauenswürdigen Systemen aufgerufen werden sollen.
    
    Verwendung in Views:
        permission_classes = [IsAdminOrHasValidAPIKey]
    """
    
    message = 'Admin-Berechtigung oder gültiger API-Key erforderlich.'
    
    def has_permission(self, request, view):
        # Prüfe Admin-Berechtigung
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        
        # Prüfe API-Key
        api_key = request.headers.get('X-API-Key') or request.headers.get('X-Api-Key')
        
        if not api_key:
            return False
        
        try:
            website = Website.objects.get(api_key=api_key, is_active=True)
            
            # Optional: Prüfe API-Secret
            api_secret = request.headers.get('X-API-Secret') or request.headers.get('X-Api-Secret')
            if api_secret and website.api_secret and api_secret != website.api_secret:
                self.message = 'API-Secret ist ungültig.'
                return False
            
            request.website = website
            return True
            
        except Website.DoesNotExist:
            self.message = 'Ungültiger API-Key.'
            return False
