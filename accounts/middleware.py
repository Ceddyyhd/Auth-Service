"""
API Request Logging Middleware
Loggt alle API-Requests mit Details wie User, IP, Endpoint, Method, etc.
"""
import json
import time
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.conf import settings
from rest_framework.exceptions import APIException
from .models import APIRequestLog

User = get_user_model()


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware zum Loggen aller API-Requests
    """
    
    def process_request(self, request):
        """
        Vor dem Request: Timestamp setzen
        """
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Nach dem Response: Log erstellen
        """
        # Nur API-Requests loggen (URLs die mit /api/ beginnen)
        # ABER NICHT Admin-Seiten oder statische Dateien
        if not request.path.startswith('/api/'):
            return response
        
        # Admin-Seiten NICHT loggen (verhindert rekursive Logs)
        if request.path.startswith('/admin/'):
            return response
        
        # Request-Dauer berechnen
        duration = None
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
        
        # User ermitteln
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        # IP-Adresse ermitteln (auch hinter Proxy)
        ip_address = self.get_client_ip(request)
        
        # Request Body auslesen (max 10000 Zeichen)
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body'):
                    body_unicode = request.body.decode('utf-8')
                    # Passwörter maskieren
                    request_body = self.mask_sensitive_data(body_unicode)
                    if len(request_body) > 10000:
                        request_body = request_body[:10000] + '... (truncated)'
            except Exception:
                request_body = '[Binary or unreadable data]'
        
        # Response Body auslesen (max 10000 Zeichen)
        response_body = None
        try:
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                # Tokens maskieren
                response_body = self.mask_sensitive_data(content)
                if len(response_body) > 10000:
                    response_body = response_body[:10000] + '... (truncated)'
        except Exception:
            response_body = '[Binary or unreadable data]'
        
        # Query Parameters
        query_params = dict(request.GET) if request.GET else None
        
        # Headers (ohne sensible Daten)
        headers = self.get_safe_headers(request)
        
        # Log in Datenbank speichern
        try:
            # Prüfe ob wir bereits im Logging sind (verhindert rekursive Aufrufe)
            if hasattr(request, '_logging_in_progress'):
                return response
            
            request._logging_in_progress = True
            
            APIRequestLog.objects.create(
                user=user,
                method=request.method,
                path=request.path,
                query_params=json.dumps(query_params) if query_params else None,
                request_body=request_body,
                response_body=response_body,
                status_code=response.status_code,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                headers=json.dumps(headers),
                duration=duration,
                referer=request.META.get('HTTP_REFERER', '')[:500]
            )
        except Exception as e:
            # Fehler beim Logging nicht durchreichen
            pass
            print(f"Error logging API request: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """
        Ermittelt die echte Client-IP (auch hinter Proxy/Load Balancer)
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Erste IP in der Liste ist die Client-IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        return ip[:45]  # IPv6 max length
    
    def mask_sensitive_data(self, text):
        """
        Maskiert sensible Daten wie Passwörter und Tokens
        """
        try:
            data = json.loads(text)
            
            # Felder die maskiert werden sollen
            sensitive_fields = [
                'password', 'password2', 'password_confirm',
                'old_password', 'new_password', 'new_password2', 'new_password_confirm',
                'access', 'refresh', 'token', 'access_token', 'refresh_token',
                'api_key', 'api_secret', 'client_secret',
                'authorization'
            ]
            
            def mask_dict(d):
                if isinstance(d, dict):
                    for key, value in d.items():
                        if key.lower() in sensitive_fields:
                            d[key] = '***MASKED***'
                        elif isinstance(value, dict):
                            mask_dict(value)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    mask_dict(item)
                return d
            
            masked_data = mask_dict(data)
            return json.dumps(masked_data, ensure_ascii=False, indent=2)
        except (json.JSONDecodeError, TypeError):
            # Kein JSON, Text zurückgeben
            return text
    
    def get_safe_headers(self, request):
        """
        Extrahiert wichtige Headers (ohne sensible Daten)
        """
        safe_headers = {}
        
        # Wichtige Headers
        important_headers = [
            'HTTP_CONTENT_TYPE',
            'HTTP_ACCEPT',
            'HTTP_ACCEPT_LANGUAGE',
            'HTTP_ACCEPT_ENCODING',
            'HTTP_ORIGIN',
            'HTTP_HOST',
            'HTTP_X_REQUESTED_WITH',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_FORWARDED_PROTO',
            'HTTP_X_REAL_IP'
        ]
        
        for header in important_headers:
            value = request.META.get(header)
            if value:
                # Präfix HTTP_ entfernen und lesbarer machen
                clean_header = header.replace('HTTP_', '').replace('_', '-').lower()
                safe_headers[clean_header] = value[:500] if isinstance(value, str) else str(value)[:500]
        
        # Remove sensitive headers
        safe_headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                # Skip authorization headers
                if 'AUTH' in key.upper() or 'TOKEN' in key.upper() or 'KEY' in key.upper():
                    safe_headers[key] = '[REDACTED]'
                else:
                    safe_headers[key] = value[:500] if isinstance(value, str) else str(value)[:500]
        
        return safe_headers


class APIExceptionHandlerMiddleware(MiddlewareMixin):
    """
    Middleware zum Abfangen aller Exceptions und Zurückgeben von JSON-Fehlern
    mit detaillierten Beschreibungen und Nutzungshinweisen
    """
    
    def process_exception(self, request, exception):
        """
        Fängt alle Exceptions ab und gibt JSON-Antworten zurück
        """
        # Nur für API-Requests
        if not request.path.startswith('/api/'):
            return None
        
        # Detaillierte Fehlerinformationen sammeln
        error_data = self.build_error_response(request, exception)
        
        # Status Code bestimmen
        status_code = getattr(exception, 'status_code', 500)
        if isinstance(exception, APIException):
            status_code = exception.status_code
        
        return JsonResponse(error_data, status=status_code, safe=False)
    
    def build_error_response(self, request, exception):
        """
        Erstellt eine detaillierte Fehlerantwort mit Nutzungshinweisen
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Basis-Fehlerstruktur
        error_data = {
            'error': True,
            'error_type': error_type,
            'message': error_message,
            'endpoint': request.path,
            'method': request.method,
        }
        
        # Füge Stack Trace hinzu wenn DEBUG=True
        if settings.DEBUG:
            error_data['traceback'] = traceback.format_exc()
        
        # Spezifische Fehlertypen mit Nutzungshinweisen
        error_data['usage_guide'] = self.get_usage_guide(request, exception)
        
        # Beispiel-Request hinzufügen
        error_data['example'] = self.get_example_request(request)
        
        return error_data
    
    def get_usage_guide(self, request, exception):
        """
        Gibt spezifische Nutzungshinweise basierend auf dem Endpunkt zurück
        """
        path = request.path
        
        # Login Endpoint
        if '/login/' in path:
            return {
                'description': 'Authentifiziert einen Benutzer und gibt JWT-Tokens zurück.',
                'required_headers': {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'Ihr API-Schlüssel (aus Website-Registrierung)'
                },
                'required_fields': {
                    'username': 'E-Mail oder Benutzername',
                    'password': 'Passwort'
                },
                'optional_fields': {
                    'mfa_token': '6-stelliger MFA-Code (nur wenn MFA aktiviert)'
                },
                'possible_errors': {
                    '400': 'Username oder Password fehlt',
                    '401': 'Ungültige Anmeldedaten',
                    '403': 'Kein Zugriff auf diese Website',
                    '500': 'Interner Serverfehler - prüfen Sie API-Key'
                }
            }
        
        # Register Endpoint
        elif '/register/' in path:
            return {
                'description': 'Erstellt einen neuen Benutzer-Account.',
                'required_headers': {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'Ihr API-Schlüssel'
                },
                'required_fields': {
                    'email': 'E-Mail-Adresse',
                    'username': 'Benutzername',
                    'password': 'Passwort',
                    'password_confirm': 'Passwortbestätigung'
                },
                'note': 'Weitere Pflichtfelder abhängig von Website-Einstellungen'
            }
        
        # Profile Endpoint
        elif '/profile/' in path:
            return {
                'description': 'Ruft Benutzerprofil ab oder aktualisiert es.',
                'required_headers': {
                    'Authorization': 'Bearer <access_token>'
                },
                'note': 'Token aus Login-Response verwenden'
            }
        
        # Permissions Endpoint
        elif '/permissions/' in path:
            return {
                'description': 'Prüft Berechtigungen für einen Benutzer.',
                'required_headers': {
                    'Authorization': 'Bearer <access_token>',
                    'X-API-Key': 'Ihr API-Schlüssel'
                },
                'note': 'Siehe PERMISSIONS_GUIDE.md für Details'
            }
        
        # Allgemeine API-Nutzung
        return {
            'description': 'Allgemeiner API-Endpunkt',
            'common_headers': {
                'Content-Type': 'application/json',
                'X-API-Key': 'API-Schlüssel (für die meisten Endpunkte)',
                'Authorization': 'Bearer <token> (für authentifizierte Endpunkte)'
            },
            'documentation': 'Siehe API_ENDPOINTS_COMPLETE.md für vollständige Dokumentation'
        }
    
    def get_example_request(self, request):
        """
        Gibt ein Beispiel-Request für den aktuellen Endpunkt zurück
        """
        path = request.path
        method = request.method
        
        # Login Beispiel
        if '/login/' in path and method == 'POST':
            return {
                'curl': (
                    'curl -X POST https://auth.palmdynamicx.de/api/accounts/login/ \\\n'
                    '  -H "Content-Type: application/json" \\\n'
                    '  -H "X-API-Key: YOUR_API_KEY" \\\n'
                    '  -d \'{"username": "user@example.com", "password": "SecurePass123!"}\''
                ),
                'javascript': (
                    'const response = await fetch("https://auth.palmdynamicx.de/api/accounts/login/", {\n'
                    '  method: "POST",\n'
                    '  headers: {\n'
                    '    "Content-Type": "application/json",\n'
                    '    "X-API-Key": "YOUR_API_KEY"\n'
                    '  },\n'
                    '  body: JSON.stringify({\n'
                    '    username: "user@example.com",\n'
                    '    password: "SecurePass123!"\n'
                    '  })\n'
                '});'
                )
            }
        
        # Register Beispiel
        elif '/register/' in path and method == 'POST':
            return {
                'curl': (
                    'curl -X POST https://auth.palmdynamicx.de/api/accounts/register/ \\\n'
                    '  -H "Content-Type: application/json" \\\n'
                    '  -H "X-API-Key: YOUR_API_KEY" \\\n'
                    '  -d \'{"email": "new@example.com", "username": "newuser", '
                    '"password": "SecurePass123!", "password_confirm": "SecurePass123!"}\''
                )
            }
        
        # Profile Beispiel
        elif '/profile/' in path:
            return {
                'curl': (
                    f'curl -X {method} https://auth.palmdynamicx.de/api/accounts/profile/ \\\n'
                    '  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"'
                )
            }
        
        return {
            'note': 'Siehe API-Dokumentation für Beispiele zu diesem Endpunkt'
        }
                safe_headers[clean_header] = value[:500]
        
        return safe_headers
