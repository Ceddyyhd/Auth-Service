from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from accounts.models import Website, SocialAccount
from accounts.serializers import (
    UserSerializer,
    SocialAccountSerializer,
    CompleteProfileSerializer,
    WebsiteRequiredFieldsSerializer
)
import secrets
import hashlib

User = get_user_model()


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
        
        return Response({
            'user': UserSerializer(user).data,
            'social_account': SocialAccountSerializer(social_account).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'created': created,
            'profile_completed': user.profile_completed,
            'message': 'Erfolgreich mit Social Login angemeldet.'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
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
    
    POST /api/accounts/complete-profile/
    Body: {
        "website_id": "uuid",
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
        serializer = CompleteProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Profil erfolgreich vervollständigt.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckProfileCompletionView(APIView):
    """
    Check if user profile is complete for a specific website.
    
    POST /api/accounts/check-profile-completion/
    Body: {
        "website_id": "uuid"
    }
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        website_id = request.data.get('website_id')
        
        if not website_id:
            return Response({
                'error': 'website_id ist erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response({
                'error': 'Website nicht gefunden.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        missing_fields = []
        
        # Check required fields
        if website.require_first_name and not user.first_name:
            missing_fields.append('first_name')
        if website.require_last_name and not user.last_name:
            missing_fields.append('last_name')
        if website.require_phone and not user.phone:
            missing_fields.append('phone')
        if website.require_address:
            if not user.street:
                missing_fields.append('street')
            if not user.street_number:
                missing_fields.append('street_number')
            if not user.city:
                missing_fields.append('city')
            if not user.postal_code:
                missing_fields.append('postal_code')
            if not user.country:
                missing_fields.append('country')
        if website.require_date_of_birth and not user.date_of_birth:
            missing_fields.append('date_of_birth')
        if website.require_company and not user.company:
            missing_fields.append('company')
        
        is_complete = len(missing_fields) == 0
        
        return Response({
            'profile_completed': is_complete,
            'missing_fields': missing_fields,
            'required_fields': WebsiteRequiredFieldsSerializer(website).data,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


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
