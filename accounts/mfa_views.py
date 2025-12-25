"""
MFA (Multi-Factor Authentication) Views
Handles TOTP-based two-factor authentication setup and verification.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import qrcode
import qrcode.image.svg
import io
import base64

from .models import MFADevice


@extend_schema(
    request=None,
    responses={
        200: {'description': 'MFA-Setup initiiert mit QR-Code und Backup-Codes'},
        400: {'description': 'MFA bereits aktiviert'}
    },
    description='Aktiviert MFA für den angemeldeten Benutzer und gibt QR-Code zurück.'
)
class EnableMFAView(APIView):
    """
    Enable MFA for the authenticated user.
    Generates a secret key and returns a QR code for scanning.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Check if MFA is already enabled
        try:
            mfa_device = MFADevice.objects.get(user=user)
            if mfa_device.is_active:
                return Response({
                    'error': 'MFA is already enabled for this account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # If device exists but not active, delete it and create new
            mfa_device.delete()
        except MFADevice.DoesNotExist:
            pass
        
        # Generate new secret
        secret_key = MFADevice.generate_secret()
        
        # Create MFA device (but not activated yet)
        mfa_device = MFADevice.objects.create(
            user=user,
            secret_key=secret_key,
            is_active=False
        )
        
        # Generate backup codes
        backup_codes = MFADevice.generate_backup_codes(count=10)
        mfa_device.set_backup_codes(backup_codes)
        mfa_device.save()
        
        # Generate QR code
        provisioning_uri = mfa_device.get_provisioning_uri(
            issuer_name=getattr(settings, 'MFA_ISSUER_NAME', 'Auth Service')
        )
        
        # Create QR code as base64 PNG
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'message': 'MFA setup initiated. Please scan the QR code with your authenticator app and verify.',
            'secret_key': secret_key,
            'qr_code': f'data:image/png;base64,{img_str}',
            'backup_codes': backup_codes,
            'manual_entry_key': secret_key,  # For manual entry if QR doesn't work
        }, status=status.HTTP_200_OK)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {
                    'type': 'string',
                    'description': '6-stelliger TOTP-Code aus der Authenticator-App',
                    'example': '123456',
                    'minLength': 6,
                    'maxLength': 6
                }
            },
            'required': ['token']
        }
    },
    responses={
        200: {'description': 'MFA erfolgreich aktiviert'},
        400: {'description': 'Ungültiger Token oder MFA noch nicht initiiert'}
    },
    description='Verifiziert das MFA-Setup durch einen TOTP-Token und aktiviert MFA.'
)
class VerifyMFASetupView(APIView):
    """
    Verify MFA setup by confirming a TOTP token.
    This activates MFA for the user.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mfa_device = MFADevice.objects.get(user=user)
        except MFADevice.DoesNotExist:
            return Response({
                'error': 'MFA setup not initiated. Please call enable endpoint first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if mfa_device.is_active:
            return Response({
                'error': 'MFA is already active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the token
        if mfa_device.verify_token(token):
            mfa_device.is_active = True
            mfa_device.activated_at = timezone.now()
            mfa_device.save()
            
            return Response({
                'message': 'MFA has been successfully enabled',
                'backup_codes_count': len(mfa_device.get_backup_codes())
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid token. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'password': {
                    'type': 'string',
                    'description': 'Aktuelles Benutzer-Passwort',
                    'format': 'password',
                    'example': 'MeinPasswort123!'
                },
                'token': {
                    'type': 'string',
                    'description': '6-stelliger TOTP-Code aus der Authenticator-App',
                    'example': '123456',
                    'minLength': 6,
                    'maxLength': 6
                }
            },
            'required': ['password', 'token']
        }
    },
    responses={
        200: {'description': 'MFA erfolgreich deaktiviert'},
        400: {'description': 'Ungültiges Passwort oder Token'}
    },
    description='Deaktiviert MFA für den Benutzer. Erfordert Passwort und MFA-Token zur Bestätigung.'
)
class DisableMFAView(APIView):
    """
    Disable MFA for the authenticated user.
    Requires password confirmation and MFA token for security.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        password = request.data.get('password')
        token = request.data.get('token')
        
        if not password:
            return Response({
                'error': 'Password is required to disable MFA'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not token:
            return Response({
                'error': 'MFA token is required to disable MFA'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not user.check_password(password):
            return Response({
                'error': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mfa_device = MFADevice.objects.get(user=user)
        except MFADevice.DoesNotExist:
            return Response({
                'error': 'MFA is not enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not mfa_device.is_active:
            return Response({
                'error': 'MFA is not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify MFA token
        if not mfa_device.verify_token(token):
            return Response({
                'error': 'Invalid MFA token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete MFA device
        mfa_device.delete()
        
        return Response({
            'message': 'MFA has been successfully disabled'
        }, status=status.HTTP_200_OK)


class RegenerateBackupCodesView(APIView):
    """
    Regenerate backup codes for the authenticated user.
    Old backup codes will be invalidated.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'MFA token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            mfa_device = MFADevice.objects.get(user=user)
        except MFADevice.DoesNotExist:
            return Response({
                'error': 'MFA is not enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not mfa_device.is_active:
            return Response({
                'error': 'MFA is not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify MFA token
        if not mfa_device.verify_token(token):
            return Response({
                'error': 'Invalid MFA token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new backup codes
        backup_codes = MFADevice.generate_backup_codes(count=10)
        mfa_device.set_backup_codes(backup_codes)
        mfa_device.save()
        
        return Response({
            'message': 'Backup codes have been regenerated',
            'backup_codes': backup_codes
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_mfa_status(request):
    """
    Get MFA status for the authenticated user.
    """
    user = request.user
    
    try:
        mfa_device = MFADevice.objects.get(user=user)
        return Response({
            'mfa_enabled': mfa_device.is_active,
            'activated_at': mfa_device.activated_at,
            'last_used': mfa_device.last_used,
            'backup_codes_count': len(mfa_device.get_backup_codes())
        })
    except MFADevice.DoesNotExist:
        return Response({
            'mfa_enabled': False,
            'activated_at': None,
            'last_used': None,
            'backup_codes_count': 0
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_mfa_token(request):
    """
    Verify an MFA token without changing any state.
    Useful for testing or re-authentication.
    """
    user = request.user
    token = request.data.get('token')
    
    if not token:
        return Response({
            'error': 'Token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        mfa_device = MFADevice.objects.get(user=user, is_active=True)
    except MFADevice.DoesNotExist:
        return Response({
            'error': 'MFA is not enabled for this account'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify token
    totp = mfa_device.get_totp()
    is_valid = totp.verify(token, valid_window=1)
    
    if is_valid:
        return Response({
            'valid': True,
            'message': 'Token is valid'
        })
    else:
        return Response({
            'valid': False,
            'message': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)
