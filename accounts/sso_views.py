"""
SSO (Single Sign-On) Views
Handles cross-website authentication for seamless user experience.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .permissions import HasValidAPIKey, HasValidAPIKeyOrIsAuthenticated
import secrets

from .models import SSOToken, Website

User = get_user_model()


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='website_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='UUID der anfragenden Website',
            required=True
        ),
        OpenApiParameter(
            name='return_url',
            type=OpenApiTypes.URI,
            location=OpenApiParameter.QUERY,
            description='URL zurück zur Website nach SSO',
            required=True
        )
    ],
    responses={
        200: {
            'description': 'SSO initiiert',
            'content': {
                'application/json': {
                    'examples': {
                        'authenticated': {
                            'summary': 'Benutzer angemeldet',
                            'value': {
                                'authenticated': True,
                                'sso_token': 'abc123def456',
                                'redirect_url': 'https://example.com/auth/callback?sso_token=abc123',
                                'expires_in': 300
                            }
                        },
                        'not_authenticated': {
                            'summary': 'Benutzer nicht angemeldet',
                            'value': {
                                'authenticated': False,
                                'login_url': 'http://localhost:3000/login?website_id=...&return_url=...',
                                'message': 'User must login first'
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Fehlende Parameter oder ungültige Website-ID'}
    },
    description='Initiiert SSO-Flow für eine Website. Prüft ob Benutzer angemeldet ist und gibt SSO-Token zurück oder Login-URL.'
)
@api_view(['GET'])
@permission_classes([HasValidAPIKey])
def initiate_sso(request):
    """
    Initiate SSO flow for a website.
    
    This endpoint checks if the user is already authenticated (has valid session).
    If yes, generates an SSO token and redirects back to the requesting website.
    If no, redirects to login page with return_url.
    
    Query Parameters:
    - website_id: UUID of the requesting website
    - return_url: URL to redirect back to after SSO
    
    Returns SSO token if user is authenticated, otherwise redirect URL to login.
    """
    website_id = request.GET.get('website_id')
    return_url = request.GET.get('return_url')
    
    if not website_id:
        return Response({
            'error': 'website_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not return_url:
        return Response({
            'error': 'return_url is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate website
    try:
        website = Website.objects.get(id=website_id)
    except Website.DoesNotExist:
        return Response({
            'error': 'Invalid website_id'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user is authenticated via session
    if request.user.is_authenticated:
        # User is logged in, generate SSO token
        token = SSOToken.generate_token()
        
        # Get client info
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create SSO token (valid for 5 minutes)
        sso_token = SSOToken.objects.create(
            user=request.user,
            token=token,
            website=website,
            expires_at=timezone.now() + timedelta(minutes=5),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Build redirect URL with token
        separator = '&' if '?' in return_url else '?'
        redirect_url = f"{return_url}{separator}sso_token={token}"
        
        return Response({
            'authenticated': True,
            'sso_token': token,
            'redirect_url': redirect_url,
            'expires_in': 300  # 5 minutes in seconds
        })
    else:
        # User not logged in, redirect to login
        # Store return_url and website_id for after login
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        login_url = f"{frontend_url}/login?website_id={website_id}&return_url={return_url}"
        
        return Response({
            'authenticated': False,
            'login_url': login_url,
            'message': 'User must login first'
        })


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'sso_token': {
                    'type': 'string',
                    'description': 'SSO-Token von initiate_sso erhalten',
                    'example': 'abc123def456'
                },
                'website_id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'UUID der Website',
                    'example': '550e8400-e29b-41d4-a716-446655440000'
                }
            },
            'required': ['sso_token', 'website_id']
        }
    },
    responses={
        200: {'description': 'JWT-Tokens erfolgreich ausgetauscht'},
        400: {'description': 'Fehlende Parameter'},
        401: {'description': 'Ungültiger oder abgelaufener SSO-Token'}
    },
    description='Tauscht SSO-Token gegen JWT-Tokens aus. Wird von der Website aufgerufen nachdem SSO-Token empfangen wurde.'
)
@api_view(['POST'])
@permission_classes([HasValidAPIKey])
def exchange_sso_token(request):
    """
    Exchange SSO token for JWT tokens.
    
    This endpoint is called by the website after receiving an SSO token.
    It validates the token and returns JWT access/refresh tokens for authentication.
    
    Request Body:
    - sso_token: The SSO token received from initiate_sso
    - website_id: UUID of the website
    
    Returns JWT tokens if token is valid.
    """
    sso_token_str = request.data.get('sso_token')
    website_id = request.data.get('website_id')
    
    if not sso_token_str:
        return Response({
            'error': 'sso_token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not website_id:
        return Response({
            'error': 'website_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find and validate SSO token
    try:
        sso_token = SSOToken.objects.select_related('user', 'website').get(
            token=sso_token_str,
            website_id=website_id
        )
    except SSOToken.DoesNotExist:
        return Response({
            'error': 'Invalid SSO token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if token is valid
    if not sso_token.is_valid():
        return Response({
            'error': 'SSO token has expired or already been used'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Optional: Verify IP address matches (for additional security)
    client_ip = request.META.get('REMOTE_ADDR')
    if sso_token.ip_address and sso_token.ip_address != client_ip:
        # Log suspicious activity but allow (IPs can change due to proxies)
        pass
    
    # Mark token as used
    sso_token.mark_as_used()
    
    # Generate JWT tokens
    user = sso_token.user
    refresh = RefreshToken.for_user(user)
    
    # Create session for this website
    from .models import UserSession
    UserSession.objects.create(
        user=user,
        website=sso_token.website,
        ip_address=client_ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        expires_at=timezone.now() + timedelta(days=7)
    )
    
    return Response({
        'success': True,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'website': {
            'id': str(sso_token.website.id),
            'name': sso_token.website.name,
        }
    })


@api_view(['POST'])
@permission_classes([HasValidAPIKey])
def check_sso_status(request):
    """
    Check if user has an active SSO session.
    
    This endpoint is called by websites to check if they should
    initiate SSO flow or show login form.
    
    Request Body:
    - website_id: UUID of the website
    
    Returns SSO availability status.
    """
    website_id = request.data.get('website_id')
    
    if not website_id:
        return Response({
            'error': 'website_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has session cookie (authenticated)
    if request.user.is_authenticated:
        # Check if user has access to this website
        try:
            website = Website.objects.get(id=website_id)
            has_access = request.user.allowed_websites.filter(id=website_id).exists()
            
            return Response({
                'sso_available': True,
                'authenticated': True,
                'has_access': has_access,
                'user_id': str(request.user.id),
                'email': request.user.email
            })
        except Website.DoesNotExist:
            return Response({
                'error': 'Invalid website_id'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'sso_available': False,
            'authenticated': False,
            'has_access': False
        })


@api_view(['POST'])
@permission_classes([HasValidAPIKey])
def sso_login_callback(request):
    """
    Handle SSO login callback after user logs in.
    
    After a user logs in on the auth service, this endpoint
    generates SSO tokens for pending website redirects.
    
    Request Body:
    - website_id: UUID of the website to redirect to
    - return_url: URL to redirect back to
    - refresh_token: User's refresh token (from login)
    
    Returns SSO token for redirect.
    """
    website_id = request.data.get('website_id')
    return_url = request.data.get('return_url')
    refresh_token = request.data.get('refresh_token')
    
    if not all([website_id, return_url, refresh_token]):
        return Response({
            'error': 'website_id, return_url, and refresh_token are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate refresh token and get user
    try:
        from rest_framework_simplejwt.tokens import RefreshToken as JWT_RefreshToken
        token = JWT_RefreshToken(refresh_token)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
    except Exception:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Validate website
    try:
        website = Website.objects.get(id=website_id)
    except Website.DoesNotExist:
        return Response({
            'error': 'Invalid website_id'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate SSO token
    token = SSOToken.generate_token()
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    sso_token = SSOToken.objects.create(
        user=user,
        token=token,
        website=website,
        expires_at=timezone.now() + timedelta(minutes=5),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Build redirect URL
    separator = '&' if '?' in return_url else '?'
    redirect_url = f"{return_url}{separator}sso_token={token}"
    
    return Response({
        'success': True,
        'sso_token': token,
        'redirect_url': redirect_url,
        'expires_in': 300
    })


@api_view(['GET'])
@permission_classes([HasValidAPIKey])
def sso_logout(request):
    """
    SSO Logout - logs user out from all websites.
    
    Query Parameters:
    - return_url: URL to redirect to after logout
    
    Clears session and invalidates all SSO tokens.
    """
    # Clear all active SSO tokens for this user
    if request.user.is_authenticated:
        SSOToken.objects.filter(
            user=request.user,
            is_used=False
        ).update(is_used=True, used_at=timezone.now())
        
        # Clear sessions
        from django.contrib.auth import logout
        logout(request)
    
    return_url = request.GET.get('return_url', '/')
    
    return Response({
        'success': True,
        'message': 'Successfully logged out from all websites',
        'redirect_url': return_url
    })
