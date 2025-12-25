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
from .models import Website, UserSession
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    WebsiteSerializer,
    WebsiteCreateSerializer,
    UserSessionSerializer
)

User = get_user_model()


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
    
    **Berechtigung:** Keine (öffentlich)
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
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
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Benutzer erfolgreich registriert.',
            'verification_email_sent': verification_sent
        }, status=status.HTTP_201_CREATED)


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
    
    **Berechtigung:** Keine (öffentlich)
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        from .models import MFADevice
        
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
                # Store temp token in session or cache (for simplicity, we'll use a short-lived approach)
                # In production, use Redis or similar
                request.session[f'mfa_temp_{temp_token}'] = {
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
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated)
    """
    permission_classes = (permissions.IsAuthenticated,)
    
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
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated)
    """
    permission_classes = (permissions.IsAuthenticated,)
    
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
    
    **Berechtigung:** Angemeldet sein (IsAuthenticated)
    """
    permission_classes = (permissions.IsAuthenticated,)
    
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
    permission_classes = (permissions.IsAdminUser,)
    
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
    permission_classes = (permissions.IsAdminUser,)


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
    
    **Berechtigung:** Admin (IsAdminUser)
    """
    permission_classes = (permissions.IsAdminUser,)
    
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
@permission_classes([permissions.IsAuthenticated])
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
            
            session, created = UserSession.objects.get_or_create(
                user=request.user,
                website=website,
                is_active=True,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'expires_at': expires_at
                }
            )
            
            if not created:
                session.last_activity = timezone.now()
                session.save()
        
        return Response({
            'has_access': has_access,
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
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSession.objects.all()
        return UserSession.objects.filter(user=self.request.user)
