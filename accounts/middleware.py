"""
API Request Logging Middleware
Loggt alle API-Requests mit Details wie User, IP, Endpoint, Method, etc.
"""
import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
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
        if not request.path.startswith('/api/'):
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
                safe_headers[clean_header] = value[:500]
        
        return safe_headers
