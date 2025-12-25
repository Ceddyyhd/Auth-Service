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
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def test_smtp_configuration(request):
    """
    Test SMTP configuration by sending a test email with detailed debugging.
    
    POST /api/accounts/test-smtp/
    Body: {
        "recipient_email": "test@example.com"
    }
    """
    import smtplib
    import socket
    
    recipient_email = request.data.get('recipient_email')
    
    if not recipient_email:
        return Response({
            'error': 'Empfänger E-Mail-Adresse ist erforderlich.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Collect configuration details
    smtp_config = {
        'backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'host_user': settings.EMAIL_HOST_USER,
        'password_configured': bool(settings.EMAIL_HOST_PASSWORD),
        'password_length': len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 0,
    }
    
    debug_info = []
    
    # Step 1: Test DNS resolution
    try:
        socket.gethostbyname(settings.EMAIL_HOST)
        debug_info.append(f"✅ DNS Resolution: {settings.EMAIL_HOST} ist erreichbar")
    except socket.gaierror as e:
        debug_info.append(f"❌ DNS Resolution Fehler: {str(e)}")
        return Response({
            'error': 'SMTP Host konnte nicht aufgelöst werden',
            'smtp_config': smtp_config,
            'debug_info': debug_info
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Step 2: Test connection
    try:
        if settings.EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            debug_info.append(f"✅ SSL Verbindung zu {settings.EMAIL_HOST}:{settings.EMAIL_PORT} erfolgreich")
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            debug_info.append(f"✅ SMTP Verbindung zu {settings.EMAIL_HOST}:{settings.EMAIL_PORT} erfolgreich")
            
            if settings.EMAIL_USE_TLS:
                server.starttls()
                debug_info.append("✅ TLS STARTTLS erfolgreich")
        
        # Step 3: Test authentication
        try:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            debug_info.append(f"✅ SMTP Authentifizierung erfolgreich für: {settings.EMAIL_HOST_USER}")
        except smtplib.SMTPAuthenticationError as e:
            error_code = e.smtp_code
            error_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            debug_info.append(f"❌ Authentifizierung fehlgeschlagen (Code {error_code}): {error_msg}")
            
            # Provide specific help based on the host
            if 'gmail' in settings.EMAIL_HOST.lower():
                debug_info.append("💡 Gmail Lösung: Verwende ein App-Passwort statt deinem normalen Passwort")
                debug_info.append("   1. Gehe zu: https://myaccount.google.com/apppasswords")
                debug_info.append("   2. Erstelle ein neues App-Passwort für 'Mail'")
                debug_info.append("   3. Verwende das 16-stellige Passwort OHNE Leerzeichen")
            elif 'outlook' in settings.EMAIL_HOST.lower() or 'office365' in settings.EMAIL_HOST.lower():
                debug_info.append("💡 Outlook/Office365 Lösung:")
                debug_info.append("   - Stelle sicher, dass SMTP AUTH aktiviert ist")
                debug_info.append("   - Verwende moderne Authentifizierung wenn möglich")
            
            server.quit()
            return Response({
                'error': f'SMTP Authentifizierung fehlgeschlagen: {error_msg}',
                'error_code': error_code,
                'smtp_config': smtp_config,
                'debug_info': debug_info,
                'troubleshooting_guide': 'Siehe EMAIL_TROUBLESHOOTING.md für detaillierte Lösungen'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 4: Send test email
        try:
            from django.core.mail import send_mail
            
            send_mail(
                subject='🧪 SMTP Test - Auth Service',
                message='Dies ist eine Test-E-Mail vom Auth Service.\n\nWenn du diese E-Mail erhältst, funktioniert die SMTP-Konfiguration korrekt!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            debug_info.append(f"✅ Test-E-Mail erfolgreich an {recipient_email} gesendet")
            
            server.quit()
            
            return Response({
                'success': True,
                'message': f'✅ SMTP Test erfolgreich! E-Mail wurde an {recipient_email} gesendet.',
                'smtp_config': smtp_config,
                'debug_info': debug_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            debug_info.append(f"❌ Fehler beim Senden der E-Mail: {str(e)}")
            server.quit()
            raise
            
    except smtplib.SMTPConnectError as e:
        debug_info.append(f"❌ Verbindungsfehler: {str(e)}")
        debug_info.append("💡 Prüfe: Firewall-Regeln, Port-Verfügbarkeit, Netzwerkverbindung")
        return Response({
            'error': f'SMTP Verbindung fehlgeschlagen: {str(e)}',
            'smtp_config': smtp_config,
            'debug_info': debug_info
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except socket.timeout:
        debug_info.append("❌ Verbindungs-Timeout")
        debug_info.append("💡 Server antwortet nicht. Prüfe: Host, Port, Firewall")
        return Response({
            'error': 'SMTP Server Timeout - keine Antwort vom Server',
            'smtp_config': smtp_config,
            'debug_info': debug_info
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    except Exception as e:
        debug_info.append(f"❌ Unerwarteter Fehler: {str(e)}")
        return Response({
            'error': f'Fehler beim SMTP Test: {str(e)}',
            'smtp_config': smtp_config,
            'debug_info': debug_info
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
