"""
Email-related views for verification and password reset.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import EmailVerificationToken, PasswordResetToken
from .email_utils import (
    send_verification_email,
    send_password_reset_email,
    send_test_email,
    send_password_changed_notification
)
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'E-Mail-Adresse des Benutzers',
                    'example': 'user@example.com'
                }
            },
            'required': ['email']
        }
    },
    responses={
        200: {'description': 'Bestätigungs-E-Mail gesendet'},
        400: {'description': 'E-Mail bereits verifiziert oder fehlt'}
    },
    description='Sendet eine neue Verifikations-E-Mail an den Benutzer.'
)
class ResendVerificationEmailView(APIView):
    """
    Resend verification email to user.
    
    POST /api/accounts/resend-verification/
    Body: {
        "email": "user@example.com"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'E-Mail-Adresse ist erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists
            return Response({
                'message': 'Wenn ein Konto mit dieser E-Mail existiert, wurde eine Bestätigungs-E-Mail gesendet.'
            }, status=status.HTTP_200_OK)
        
        if user.is_verified:
            return Response({
                'error': 'E-Mail-Adresse ist bereits verifiziert.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new verification token
        token = EmailVerificationToken.generate_token()
        expires_at = timezone.now() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS)
        
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send verification email
        try:
            send_verification_email(user, token)
            return Response({
                'message': 'Bestätigungs-E-Mail wurde gesendet.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Fehler beim Senden der E-Mail: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {
                    'type': 'string',
                    'description': 'Email-Verifizierungs-Token aus der Bestätigungs-E-Mail',
                    'example': 'abc123def456'
                }
            },
            'required': ['token']
        }
    },
    responses={
        200: {'description': 'E-Mail erfolgreich verifiziert'},
        400: {'description': 'Ungültiger oder abgelaufener Token'}
    },
    description='Verifiziert die E-Mail-Adresse des Benutzers mit einem Token.'
)
class VerifyEmailView(APIView):
    """
    Verify user email with token.
    
    POST /api/accounts/verify-email/
    Body: {
        "token": "verification_token"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        token_str = request.data.get('token')
        
        if not token_str:
            return Response({
                'error': 'Token ist erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = EmailVerificationToken.objects.get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response({
                'error': 'Ungültiger Token.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not token.is_valid():
            return Response({
                'error': 'Token ist abgelaufen oder wurde bereits verwendet.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        # Verify user email
        user = token.user
        user.is_verified = True
        user.save()
        
        return Response({
            'message': 'E-Mail erfolgreich verifiziert.',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'is_verified': user.is_verified
            }
        }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'E-Mail-Adresse des Benutzers',
                    'example': 'user@example.com'
                }
            },
            'required': ['email']
        }
    },
    responses={
        200: {'description': 'Passwort-Reset-E-Mail gesendet'},
        400: {'description': 'E-Mail fehlt'}
    },
    description='Sendet eine Passwort-Reset-E-Mail an den Benutzer.'
)
class RequestPasswordResetView(APIView):
    """
    Request password reset email.
    
    POST /api/accounts/request-password-reset/
    Body: {
        "email": "user@example.com"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'E-Mail-Adresse ist erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if user exists
            return Response({
                'message': 'Wenn ein Konto mit dieser E-Mail existiert, wurde eine Passwort-Reset-E-Mail gesendet.'
            }, status=status.HTTP_200_OK)
        
        # Create password reset token
        token = PasswordResetToken.generate_token()
        expires_at = timezone.now() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS)
        
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send password reset email
        try:
            send_password_reset_email(user, token)
            return Response({
                'message': 'Passwort-Reset-E-Mail wurde gesendet.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Fehler beim Senden der E-Mail: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset."""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Passwörter stimmen nicht überein."
            })
        return attrs


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {
                    'type': 'string',
                    'description': 'Passwort-Reset-Token aus der E-Mail',
                    'example': 'abc123def456'
                },
                'new_password': {
                    'type': 'string',
                    'format': 'password',
                    'description': 'Neues Passwort (mind. 8 Zeichen)',
                    'example': 'NeuesPa$$w0rt123'
                },
                'new_password2': {
                    'type': 'string',
                    'format': 'password',
                    'description': 'Neues Passwort (Bestätigung)',
                    'example': 'NeuesPa$$w0rt123'
                }
            },
            'required': ['token', 'new_password', 'new_password2']
        }
    },
    responses={
        200: {'description': 'Passwort erfolgreich zurückgesetzt'},
        400: {'description': 'Ungültiger Token oder Passwörter stimmen nicht überein'}
    },
    description='Setzt das Passwort zurück mit einem Token aus der Reset-E-Mail.'
)
class ResetPasswordView(APIView):
    """
    Reset password with token.
    
    POST /api/accounts/reset-password/
    Body: {
        "token": "reset_token",
        "new_password": "NewPassword123!",
        "new_password2": "NewPassword123!"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            token = PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Ungültiger Token.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not token.is_valid():
            return Response({
                'error': 'Token ist abgelaufen oder wurde bereits verwendet.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        # Reset password
        user = token.user
        user.set_password(new_password)
        user.save()
        
        # Send notification email
        try:
            send_password_changed_notification(user)
        except:
            pass  # Don't fail if notification email fails
        
        return Response({
            'message': 'Passwort erfolgreich zurückgesetzt.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def test_smtp_configuration(request):
    """
    Test SMTP configuration by sending a test email.
    
    POST /api/accounts/test-smtp/
    Body: {
        "recipient_email": "test@example.com"
    }
    """
    recipient_email = request.data.get('recipient_email')
    
    if not recipient_email:
        return Response({
            'error': 'Empfänger E-Mail-Adresse ist erforderlich.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        send_test_email(recipient_email)
        return Response({
            'message': f'Test-E-Mail erfolgreich an {recipient_email} gesendet.',
            'smtp_config': {
                'host': settings.EMAIL_HOST,
                'port': settings.EMAIL_PORT,
                'use_tls': settings.EMAIL_USE_TLS,
                'use_ssl': settings.EMAIL_USE_SSL,
                'from_email': settings.DEFAULT_FROM_EMAIL
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Fehler beim Senden der Test-E-Mail: {str(e)}',
            'smtp_config': {
                'host': settings.EMAIL_HOST,
                'port': settings.EMAIL_PORT,
                'use_tls': settings.EMAIL_USE_TLS,
                'use_ssl': settings.EMAIL_USE_SSL,
                'from_email': settings.DEFAULT_FROM_EMAIL
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_smtp_configuration(request):
    """
    Get current SMTP configuration (without sensitive data).
    
    GET /api/accounts/smtp-config/
    """
    return Response({
        'email_backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': settings.EMAIL_USE_SSL,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'host_user': settings.EMAIL_HOST_USER,
        'host_password_configured': bool(settings.EMAIL_HOST_PASSWORD),
        'verification_token_expiry_hours': settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS,
        'password_reset_token_expiry_hours': settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS,
    }, status=status.HTTP_200_OK)
