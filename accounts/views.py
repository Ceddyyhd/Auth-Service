from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Website, UserSession, MFADevice
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    WebsiteSerializer,
    WebsiteCreateSerializer,
    UserSessionSerializer
)
from .permissions import HasValidAPIKey, HasValidAPIKeyOrIsAuthenticated, IsAdminOrHasValidAPIKey

User = get_user_model()

# Simple in-memory storage for MFA temporary tokens
# In production, this could be replaced with Redis or database-backed cache
_mfa_temp_tokens = {}


class RegisterView(generics.CreateAPIView):
    """
    👤 Benutzer-Registrierung
    
    Erstellt einen neuen Benutzer-Account. Pflichtfelder werden basierend
    auf den Website-Einstellungen validiert.
    
    **Endpoint:** POST /api/accounts/register/
    
    **Beispiel Request:**
    ```json
    {
      "email": "user@example.com",
      "username": "user123",
      "password": "SecurePassword123!",
      "password_confirm": "SecurePassword123!",
      "first_name": "Max",
      "last_name": "Mustermann",
      "website_id": "website-uuid",
      
      // Optional, abhängig von Website-Pflichtfeldern:
      "phone": "+49123456789",
      "street": "Musterstraße",
      "street_number": "123",
      "city": "Berlin",
      "postal_code": "10115",
      "country": "Deutschland",
      "date_of_birth": "1990-01-01",
      "company": "Meine Firma GmbH"
    }
    ```
    
    **Response (201 Created):**
    ```json
    {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "username": "user123",
        "first_name": "Max",
        "last_name": "Mustermann",
        "profile_completed": true,
        "is_verified": false
      },
      "tokens": {
        "refresh": "eyJ...",
        "access": "eyJ..."
      },
      "message": "Benutzer erfolgreich registriert."
    }
    ```
    
    **Frontend Beispiel (JavaScript):**
    ```javascript
    async function register(userData) {
      const response = await fetch('http://localhost:8000/api/accounts/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      const data = await response.json();
      
      // Tokens im localStorage speichern
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      
      return data;
    }
    ```
    
    **Pflichtfelder:**
    - Immer: email, username, password, password_confirm, website_id
    - Je nach Website-Einstellung: first_name, last_name, phone, address, date_of_birth, company
    
    **Berechtigung:** API-Key erforderlich (X-API-Key Header)
    """
    queryset = User.objects.all()
    permission_classes = [HasValidAPIKey]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        # Füge website_id hinzu, wenn API-Key verwendet wird
        if hasattr(request, 'website') and 'website_id' not in request.data:
            # Create a mutable copy of request data
            data = request.data.copy()
            data['website_id'] = str(request.website.id)
            serializer = self.get_serializer(data=data)
        else:
            serializer = self.get_serializer(data=request.data)
            
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Send verification email
        from .models import EmailVerificationToken
        from .email_utils import send_verification_email
        from django.conf import settings
        from datetime import timedelta
        
        token = EmailVerificationToken.generate_token()
        expires_at = timezone.now() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS)
        
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        try:
            send_verification_email(user, token)
            verification_sent = True
        except Exception as e:
            verification_sent = False
        
        # Erstelle Lexware-Kontakt (nur wenn Daten vollständig genug sind)
        lexware_customer_number = None
        lexware_error = None
        try:
            from .lexware_integration import get_lexware_client, LexwareAPIError
            lexware = get_lexware_client()
            
            # Prüfe ob Daten für Lexware-Kontakt ausreichend sind
            is_valid, error_msg = lexware.validate_user_data(user)
            
            if is_valid:
                # Daten sind vollständig - erstelle Kontakt
                contact = lexware.create_customer_contact(user)
                lexware_customer_number = user.lexware_customer_number
            else:
                # Daten unvollständig - nur loggen, nicht blockieren
                import logging
                logger = logging.getLogger(__name__)
                logger.info(
                    f"Lexware-Kontakt für {user.email} übersprungen: {error_msg}. "
                    "Kann später nachträglich erstellt werden."
                )
                lexware_error = "Profil unvollständig für Lexware (kann später nachgeholt werden)"
        except LexwareAPIError as e:
            # Logge Fehler, aber blockiere Registrierung nicht
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Fehler beim Erstellen des Lexware-Kontakts für {user.email}: {str(e)}")
            lexware_error = "Lexware-Kontakt konnte nicht erstellt werden"
        except Exception as e:
            # Bei fehlender Konfiguration oder anderen Fehlern
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Lexware-Integration übersprungen für {user.email}: {str(e)}")
        
        # Create session for the website (if API-Key was used)
        if hasattr(request, 'website'):
            expires_at = timezone.now() + timedelta(hours=24)
            UserSession.objects.update_or_create(
                user=user,
                website=request.website,
                is_active=True,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'expires_at': expires_at
                }
            )
        
        response_data = {
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Benutzer erfolgreich registriert.',
            'verification_email_sent': verification_sent
        }
        
        # Füge Lexware-Kundennummer hinzu wenn vorhanden
        if lexware_customer_number:
            response_data['lexware_customer_number'] = lexware_customer_number
        if lexware_error:
            response_data['lexware_warning'] = lexware_error
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    🔐 Benutzer-Login (mit MFA-Unterstützung)
    
    Authentifiziert einen Benutzer und gibt JWT-Tokens zurück.
    Wenn MFA aktiviert ist, wird ein temporärer Token zurückgegeben, 
    der mit einem MFA-Code verifiziert werden muss.
    
    **Endpoint:** POST /api/accounts/login/
    
    **Request:**
    ```json
    {
      "username": "user@example.com",  // oder username
      "password": "SecurePassword123!",
      "mfa_token": "123456"  // Optional: nur wenn MFA aktiviert ist
    }
    ```
    
    **Response ohne MFA (200 OK):**
    ```json
    {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    ```
    
    **Response mit MFA aktiviert (200 OK):**
    ```json
    {
      "mfa_required": true,
      "temp_token": "temporary_token_for_mfa_verification",
      "message": "MFA verification required"
    }
    ```
    
    **Response (401 Unauthorized):**
    ```json
    {
      "detail": "No active account found with the given credentials"
    }
    ```
    
    **Frontend Beispiel (JavaScript):**
    ```javascript
    async function login(email, password, mfaToken = null) {
      const body = { username: email, password };
      if (mfaToken) body.mfa_token = mfaToken;
      
      const response = await fetch('http://localhost:8000/api/accounts/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      if (!response.ok) throw new Error('Login fehlgeschlagen');
      
      const data = await response.json();
      
      // Check if MFA is required
      if (data.mfa_required) {
        // Show MFA input form
        return { mfaRequired: true, tempToken: data.temp_token };
      }
      
      // Tokens speichern
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      return data;
    }
    ```
    
    **Token verwenden:**
    ```javascript
    fetch('http://localhost:8000/api/accounts/profile/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    ```
    
    **Berechtigung:** API-Key erforderlich (X-API-Key Header)
    """
    permission_classes = [HasValidAPIKey]
    
    def post(self, request, *args, **kwargs):
        # Get username/email and password
        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        mfa_token = request.data.get('mfa_token')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response({
                'detail': 'No active account found with the given credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if MFA is enabled
        try:
            mfa_device = MFADevice.objects.get(user=user, is_active=True)
            
            # MFA is enabled, check if token is provided
            if not mfa_token:
                # Generate temporary token for MFA verification
                temp_token = secrets.token_urlsafe(32)
                
                # Store temp token (clean old tokens first)
                global _mfa_temp_tokens
                # Remove expired tokens (older than 5 minutes)
                current_time = timezone.now()
                _mfa_temp_tokens = {
                    k: v for k, v in _mfa_temp_tokens.items()
                    if (current_time - timezone.datetime.fromisoformat(v['timestamp'])).total_seconds() < 300
                }
                
                # Store new token
                _mfa_temp_tokens[f'mfa_temp_{temp_token}'] = {
                    'user_id': str(user.id),
                    'timestamp': timezone.now().isoformat()
                }
                
                return Response({
                    'mfa_required': True,
                    'temp_token': temp_token,
                    'message': 'MFA verification required'
                }, status=status.HTTP_200_OK)
            
            # MFA token provided, verify it
            if not mfa_device.verify_token(mfa_token):
                return Response({
                    'error': 'Invalid MFA token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # MFA verified, proceed with login
        except MFADevice.DoesNotExist:
            # No MFA enabled, proceed with normal login
            pass
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        # Grant website access and create session (if API-Key was used)
        if hasattr(request, 'website'):
            # Prüfe ob Website-Zugriff erforderlich ist
            if request.website.require_website_access:
                # Website verlangt expliziten Zugriff - prüfe Berechtigung
                if request.website.auto_register_users or user.has_website_access(request.website):
                    if not user.has_website_access(request.website):
                        user.allowed_websites.add(request.website)
                else:
                    # User hat keinen Zugriff auf diese Website
                    return Response({
                        'error': 'Sie haben keinen Zugriff auf diese Website.',
                        'website': request.website.name
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                # Website erlaubt Login für alle - gewähre automatisch Zugriff
                if not user.has_website_access(request.website):
                    user.allowed_websites.add(request.website)
            
            # Create or update session
            expires_at = timezone.now() + timedelta(hours=24)
            UserSession.objects.update_or_create(
                user=user,
                website=request.website,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {
                    'type': 'string',
                    'description': 'JWT Refresh Token',
                    'example': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                }
            },
            'required': ['refresh']
        }
    },
    responses={200: {'description': 'Erfolgreich abgemeldet'}},
    description='Invalidiert den Refresh-Token und meldet den Benutzer ab.'
)
class LogoutView(APIView):
    """
    🚪 Benutzer-Logout
    
    Invalidiert den Refresh-Token und meldet den Benutzer ab.
    
    **Endpoint:** POST /api/accounts/logout/
    
    **Headers erforderlich:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Request:**
    ```json
    {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    ```
    
    **Response (200 OK):**
    ```json
    {
      "message": "Erfolgreich abgemeldet."
    }
    ```
    
    **Frontend Beispiel (JavaScript):**
    ```javascript
    async function logout() {
      const refreshToken = localStorage.getItem('refresh_token');
      
      await fetch('http://localhost:8000/api/accounts/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ refresh: refreshToken })
      });
      
      // Tokens entfernen
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Zur Login-Seite weiterleiten
      window.location.href = '/login';
    }
    ```
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated) oder API-Key
    """
    permission_classes = [HasValidAPIKeyOrIsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                "message": "Erfolgreich abgemeldet."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Fehler beim Abmelden."
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    👤 Benutzerprofil anzeigen und bearbeiten
    
    Ruft die Profildaten des angemeldeten Benutzers ab oder aktualisiert sie.
    
    **Endpoints:**
    - GET /api/accounts/profile/ - Profil abrufen
    - PUT /api/accounts/profile/ - Profil aktualisieren
    - PATCH /api/accounts/profile/ - Profil teilweise aktualisieren
    
    **Headers erforderlich:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Response (GET 200 OK):**
    ```json
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "user123",
      "first_name": "Max",
      "last_name": "Mustermann",
      "phone": "+49123456789",
      "street": "Musterstraße",
      "street_number": "123",
      "city": "Berlin",
      "postal_code": "10115",
      "country": "Deutschland",
      "date_of_birth": "1990-01-01",
      "company": "Meine Firma GmbH",
      "profile_completed": true,
      "is_verified": true,
      "is_active": true,
      "date_joined": "2025-01-01T10:00:00Z"
    }
    ```
    
    **Request (PUT/PATCH):**
    ```json
    {
      "first_name": "Maximilian",
      "last_name": "Mustermann",
      "phone": "+49987654321",
      "city": "München"
    }
    ```
    
    **Frontend Beispiel (JavaScript):**
    ```javascript
    // Profil abrufen
    async function getProfile() {
      const response = await fetch('http://localhost:8000/api/accounts/profile/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      return await response.json();
    }
    
    // Profil aktualisieren
    async function updateProfile(updates) {
      const response = await fetch('http://localhost:8000/api/accounts/profile/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(updates)
      });
      return await response.json();
    }
    ```
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated) oder API-Key
    """
    permission_classes = [HasValidAPIKeyOrIsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


@extend_schema(
    request=ChangePasswordSerializer,
    responses={
        200: {'description': 'Passwort erfolgreich geändert'},
        400: {'description': 'Ungültige Daten oder altes Passwort falsch'}
    },
    description='Ändert das Passwort des angemeldeten Benutzers. Erfordert altes Passwort, neues Passwort und Bestätigung des neuen Passworts.'
)
class ChangePasswordView(APIView):
    """
    🔒 Passwort ändern
    
    Ändert das Passwort des angemeldeten Benutzers.
    
    **Endpoint:** POST /api/accounts/change-password/
    
    **Headers erforderlich:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Request Body:**
    ```json
    {
      "old_password": "AltesPa$$w0rt",
      "new_password": "NeuesPa$$w0rt123",
      "new_password2": "NeuesPa$$w0rt123"
    }
    ```
    
    **Response (200 OK):**
    ```json
    {
      "message": "Passwort erfolgreich geändert."
    }
    ```
    
    **Response (400 Bad Request):**
    ```json
    {
      "error": "Altes Passwort ist falsch."
    }
    ```
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated) oder API-Key
    """
    permission_classes = [HasValidAPIKeyOrIsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Altes Passwort ist falsch.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Passwort erfolgreich geändert.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WebsiteListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create websites.
    
    GET /api/accounts/websites/
    POST /api/accounts/websites/
    """
    queryset = Website.objects.all()
    permission_classes = [IsAdminOrHasValidAPIKey]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WebsiteCreateSerializer
        return WebsiteSerializer


class WebsiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a website.
    
    GET /api/accounts/websites/{id}/
    PUT /api/accounts/websites/{id}/
    DELETE /api/accounts/websites/{id}/
    """
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [IsAdminOrHasValidAPIKey]


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'website_id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'UUID der Website',
                    'example': '550e8400-e29b-41d4-a716-446655440000'
                }
            },
            'required': ['website_id']
        }
    },
    responses={
        200: {'description': 'Zugriff erfolgreich gewährt oder entfernt'},
        404: {'description': 'Benutzer oder Website nicht gefunden'}
    },
    description='Verwaltet den Zugriff von Benutzern auf Websites.'
)
class UserWebsiteAccessView(APIView):
    """
    🌐 Benutzer-Website-Zugriff verwalten
    
    Gewährt oder entzieht Benutzern Zugriff auf Websites.
    
    **Endpoints:**
    - POST /api/accounts/users/{user_id}/websites/ - Zugriff gewähren
    - DELETE /api/accounts/users/{user_id}/websites/ - Zugriff entziehen
    
    **Request Body:**
    ```json
    {
      "website_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    
    **Berechtigung:** Admin (IsAdminUser) oder API-Key
    """
    permission_classes = [IsAdminOrHasValidAPIKey]
    
    def post(self, request, user_id):
        """Grant user access to a website."""
        try:
            user = User.objects.get(id=user_id)
            website_id = request.data.get('website_id')
            website = Website.objects.get(id=website_id)
            
            user.allowed_websites.add(website)
            
            return Response({
                'message': f'Zugriff für {user.email} auf {website.name} gewährt.'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Benutzer nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Website.DoesNotExist:
            return Response({'error': 'Website nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, user_id):
        """Revoke user access to a website."""
        try:
            user = User.objects.get(id=user_id)
            website_id = request.data.get('website_id')
            website = Website.objects.get(id=website_id)
            
            user.allowed_websites.remove(website)
            
            return Response({
                'message': f'Zugriff für {user.email} auf {website.name} entfernt.'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Benutzer nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Website.DoesNotExist:
            return Response({'error': 'Website nicht gefunden.'}, 
                          status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'website_id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'UUID der Website',
                    'example': '550e8400-e29b-41d4-a716-446655440000'
                }
            },
            'required': ['website_id']
        }
    },
    responses={
        200: {'description': 'Zugriff verifiziert'},
        404: {'description': 'Website nicht gefunden'}
    },
    description='Verifiziert, ob der Benutzer Zugriff auf eine bestimmte Website hat.'
)
@api_view(['POST'])
@permission_classes([HasValidAPIKeyOrIsAuthenticated])
def verify_access(request):
    """
    Verify if user has access to a specific website.
    
    POST /api/accounts/verify-access/
    Body: {"website_id": "uuid"}
    """
    website_id = request.data.get('website_id')
    
    try:
        website = Website.objects.get(id=website_id, is_active=True)
        has_access = request.user.has_website_access(website)
        
        if has_access:
            # Create or update session
            expires_at = timezone.now() + timedelta(hours=24)
            
            session, created = UserSession.objects.update_or_create(
                user=request.user,
                website=website,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            
            # Update last_activity if not created
            if not created:
                session.last_activity = timezone.now()
                session.expires_at = expires_at  # Extend session
                session.save()
            
            # Prüfe ob Session abgelaufen ist
            session_valid = not session.is_expired()
        else:
            session_valid = False
        
        return Response({
            'has_access': has_access,
            'session_valid': session_valid if has_access else False,
            'user': UserSerializer(request.user).data,
            'website': WebsiteSerializer(website).data
        }, status=status.HTTP_200_OK)
    
    except Website.DoesNotExist:
        return Response({
            'error': 'Website nicht gefunden oder nicht aktiv.'
        }, status=status.HTTP_404_NOT_FOUND)


class UserSessionListView(generics.ListAPIView):
    """
    API endpoint to list user sessions.
    
    GET /api/accounts/sessions/
    """
    serializer_class = UserSessionSerializer
    permission_classes = [HasValidAPIKeyOrIsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSession.objects.all()
        return UserSession.objects.filter(user=self.request.user)
