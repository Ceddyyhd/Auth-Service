from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from accounts.models import Website, SocialAccount
from accounts.serializers import (
    UserSerializer,
    SocialAccountSerializer,
    CompleteProfileSerializer,
    WebsiteRequiredFieldsSerializer
)
from accounts.lexware_integration import get_lexware_client
import secrets
import hashlib
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'provider': {
                    'type': 'string',
                    'enum': ['google', 'facebook', 'github', 'microsoft', 'apple'],
                    'description': 'Social Login Provider',
                    'example': 'google'
                },
                'provider_user_id': {
                    'type': 'string',
                    'description': 'Benutzer-ID vom Provider',
                    'example': '1234567890'
                },
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'E-Mail-Adresse vom Provider',
                    'example': 'user@example.com'
                },
                'first_name': {
                    'type': 'string',
                    'description': 'Vorname (optional)',
                    'example': 'Max'
                },
                'last_name': {
                    'type': 'string',
                    'description': 'Nachname (optional)',
                    'example': 'Mustermann'
                },
                'avatar_url': {
                    'type': 'string',
                    'format': 'uri',
                    'description': 'Profilbild-URL (optional)',
                    'example': 'https://example.com/avatar.jpg'
                },
                'access_token': {
                    'type': 'string',
                    'description': 'Access Token vom Provider',
                    'example': 'ya29.a0AfH6SMB...'
                }
            },
            'required': ['provider', 'provider_user_id', 'email']
        }
    },
    responses={
        200: {'description': 'Erfolgreich eingeloggt'},
        400: {'description': 'Fehlende erforderliche Felder'}
    },
    description='Behandelt Social Login (Google, Facebook, GitHub, etc.).'
)
class SocialLoginView(APIView):
    """
    Handle social login (Google, Facebook, GitHub, etc.).
    
    POST /api/accounts/social-login/
    Body: {
        "provider": "google",
        "provider_user_id": "1234567890",
        "email": "user@example.com",
        "first_name": "Max",
        "last_name": "Mustermann",
        "avatar_url": "https://...",
        "access_token": "provider_access_token"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        provider = request.data.get('provider')
        provider_user_id = request.data.get('provider_user_id')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        avatar_url = request.data.get('avatar_url', '')
        
        if not all([provider, provider_user_id, email]):
            return Response({
                'error': 'provider, provider_user_id und email sind erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if social account exists
        try:
            social_account = SocialAccount.objects.get(
                provider=provider,
                provider_user_id=provider_user_id
            )
            user = social_account.user
            created = False
        except SocialAccount.DoesNotExist:
            # Check if user with this email exists
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                # Create new user
                username = self._generate_unique_username(email)
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_verified=True  # Email already verified by provider
                )
                created = True
            
            # Create social account link
            social_account = SocialAccount.objects.create(
                user=user,
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'user': UserSerializer(user).data,
            'social_account': SocialAccountSerializer(social_account).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'created': created,
            'profile_completed': user.profile_completed,
            'message': 'Erfolgreich mit Social Login angemeldet.'
        }
        
        # Prüfe Lexware-Bereitschaft und gebe Hinweise
        if not user.is_ready_for_lexware():
            missing = user.get_lexware_missing_fields()
            response_data['lexware_ready'] = False
            response_data['lexware_missing_fields'] = missing
            response_data['lexware_info'] = (
                f"Profil unvollständig für Kundenkonto. "
                f"Fehlende Felder: {', '.join(missing)}"
            )
        else:
            response_data['lexware_ready'] = True
            if user.lexware_customer_number:
                response_data['lexware_customer_number'] = user.lexware_customer_number
        
        return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    def _generate_unique_username(self, email):
        """Generate unique username from email."""
        base_username = email.split('@')[0]
        username = base_username
        
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username


class CompleteProfileView(APIView):
    """
    Complete user profile with missing required fields.
    Automatically creates Lexware contact if profile becomes complete.
    
    POST /api/accounts/complete-profile/
    Body: {
        "first_name": "Max",
        "last_name": "Mustermann",
        "phone": "+49123456789",
        "street": "Musterstraße",
        "street_number": "123",
        "city": "Berlin",
        "postal_code": "10115",
        "country": "Deutschland",
        "date_of_birth": "1990-01-01",
        "company": "Musterfirma GmbH"
    }
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        user = request.user
        had_lexware_contact = bool(user.lexware_contact_id)
        
        serializer = CompleteProfileSerializer(
            user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            user = serializer.save()
            
            response_data = {
                'user': UserSerializer(user).data,
                'message': 'Profil erfolgreich vervollständigt.'
            }
            
            # Versuche Lexware-Kontakt zu erstellen, falls noch nicht vorhanden
            if not had_lexware_contact and user.is_ready_for_lexware():
                try:
                    lexware = get_lexware_client()
                    if lexware:
                        contact = lexware.create_customer_contact(user)
                        if contact:
                            response_data['lexware_created'] = True
                            response_data['lexware_customer_number'] = user.lexware_customer_number
                            logger.info(
                                f"Lexware-Kontakt erstellt nach Profil-Vervollständigung: "
                                f"{user.email} (Kundennummer: {user.lexware_customer_number})"
                            )
                        else:
                            response_data['lexware_created'] = False
                            response_data['lexware_info'] = 'Lexware-Kontakt konnte nicht erstellt werden.'
                    else:
                        response_data['lexware_created'] = False
                        response_data['lexware_info'] = 'Lexware-Integration nicht konfiguriert.'
                except Exception as e:
                    logger.error(f"Fehler bei Lexware-Kontakt-Erstellung nach complete-profile: {str(e)}")
                    response_data['lexware_created'] = False
                    response_data['lexware_info'] = 'Fehler bei Lexware-Kontakt-Erstellung.'
            elif had_lexware_contact:
                # Aktualisiere existierenden Kontakt
                try:
                    lexware = get_lexware_client()
                    if lexware:
                        lexware.update_customer_contact(user)
                        response_data['lexware_updated'] = True
                        logger.info(f"Lexware-Kontakt aktualisiert: {user.email}")
                except Exception as e:
                    logger.error(f"Fehler bei Lexware-Kontakt-Aktualisierung: {str(e)}")
                    response_data['lexware_updated'] = False
            elif not user.is_ready_for_lexware():
                missing = user.get_lexware_missing_fields()
                response_data['lexware_info'] = f"Profil noch unvollständig für Lexware: {', '.join(missing)}"
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckProfileCompletionView(APIView):
    """
    Check if user profile is complete.
    
    General profile completion check (Lexware-ready).
    Optionally check website-specific requirements if website_id provided.
    
    GET or POST /api/accounts/check-profile-completion/
    Body (optional): {
        "website_id": "uuid"  // Optional: für website-spezifische Prüfung
    }
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        """GET endpoint für allgemeine Profil-Prüfung."""
        return self._check_profile(request)
    
    def post(self, request):
        """POST endpoint für optionale website-spezifische Prüfung."""
        return self._check_profile(request)
    
    def _check_profile(self, request):
        user = request.user
        website_id = request.data.get('website_id') if request.method == 'POST' else None
        
        # Allgemeine Profil-Prüfung (Lexware-Bereitschaft)
        is_lexware_ready = user.is_ready_for_lexware()
        lexware_missing = user.get_lexware_missing_fields()
        
        response_data = {
            'profile_completed': is_lexware_ready,
            'missing_fields': lexware_missing,
            'has_lexware_contact': bool(user.lexware_contact_id),
            'lexware_customer_number': user.lexware_customer_number,
            'user': UserSerializer(user).data
        }
        
        # Optional: Website-spezifische Prüfung
        if website_id:
            try:
                website = Website.objects.get(id=website_id)
                website_missing = []
                
                # Check required fields
                if website.require_first_name and not user.first_name:
                    website_missing.append('first_name')
                if website.require_last_name and not user.last_name:
                    website_missing.append('last_name')
                if website.require_phone and not user.phone:
                    website_missing.append('phone')
                if website.require_address:
                    if not user.street:
                        website_missing.append('street')
                    if not user.street_number:
                        website_missing.append('street_number')
                    if not user.city:
                        website_missing.append('city')
                    if not user.postal_code:
                        website_missing.append('postal_code')
                    if not user.country:
                        website_missing.append('country')
                if website.require_date_of_birth and not user.date_of_birth:
                    website_missing.append('date_of_birth')
                if website.require_company and not user.company:
                    website_missing.append('company')
                
                response_data['website_check'] = {
                    'website_id': str(website.id),
                    'website_name': website.name,
                    'profile_completed': len(website_missing) == 0,
                    'missing_fields': website_missing,
                    'required_fields': WebsiteRequiredFieldsSerializer(website).data
                }
            except Website.DoesNotExist:
                response_data['website_check_error'] = 'Website nicht gefunden.'
        
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_social_accounts(request):
    """
    Get all social accounts linked to current user.
    
    GET /api/accounts/social-accounts/
    """
    social_accounts = SocialAccount.objects.filter(user=request.user)
    serializer = SocialAccountSerializer(social_accounts, many=True)
    
    return Response({
        'social_accounts': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unlink_social_account(request, provider):
    """
    Unlink a social account.
    
    DELETE /api/accounts/social-accounts/{provider}/
    """
    try:
        social_account = SocialAccount.objects.get(
            user=request.user,
            provider=provider
        )
        social_account.delete()
        
        return Response({
            'message': f'{provider} Account erfolgreich entfernt.'
        }, status=status.HTTP_200_OK)
    except SocialAccount.DoesNotExist:
        return Response({
            'error': 'Social Account nicht gefunden.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_website_required_fields(request, website_id):
    """
    Get required fields configuration for a website.
    
    GET /api/accounts/websites/{website_id}/required-fields/
    """
    website = get_object_or_404(Website, id=website_id)
    serializer = WebsiteRequiredFieldsSerializer(website)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
