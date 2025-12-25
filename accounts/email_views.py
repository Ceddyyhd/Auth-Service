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
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Email-Verifizierungs-Token aus der Bestätigungs-E-Mail (für GET)',
        ),
    ],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {
                    'type': 'string',
                    'description': 'Email-Verifizierungs-Token aus der Bestätigungs-E-Mail (für POST)',
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
    description='Verifiziert die E-Mail-Adresse des Benutzers mit einem Token. Unterstützt GET (Query-Parameter) und POST (JSON Body).'
)
class VerifyEmailView(APIView):
    """
    Verify user email with token.
    
    GET /api/accounts/verify-email/?token=verification_token (für E-Mail-Links)
    POST /api/accounts/verify-email/ (für API-Calls)
    Body: {
        "token": "verification_token"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        """Handle GET request from email link"""
        token_str = request.GET.get('token')
        
        if not token_str:
            return self._render_html_response(
                success=False,
                title="Token fehlt",
                message="Kein Verifizierungs-Token gefunden.",
                details="Bitte verwende den Link aus der Bestätigungs-E-Mail."
            )
        
        result = self._verify_token(token_str)
        
        if result['success']:
            return self._render_html_response(
                success=True,
                title="E-Mail verifiziert",
                message="Deine E-Mail-Adresse wurde erfolgreich bestätigt!",
                details=f"Du kannst dich jetzt mit {result['email']} anmelden."
            )
        else:
            return self._render_html_response(
                success=False,
                title="Verifizierung fehlgeschlagen",
                message=result['error'],
                details="Bitte fordere eine neue Bestätigungs-E-Mail an."
            )
    
    def post(self, request):
        """Handle POST request from API"""
        token_str = request.data.get('token')
        
        if not token_str:
            return Response({
                'error': 'Token ist erforderlich.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = self._verify_token(token_str)
        
        if result['success']:
            return Response({
                'message': 'E-Mail erfolgreich verifiziert.',
                'user': {
                    'id': result['user_id'],
                    'email': result['email'],
                    'is_verified': True
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _verify_token(self, token_str):
        """Common token verification logic"""
        try:
            token = EmailVerificationToken.objects.get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return {
                'success': False,
                'error': 'Ungültiger Token.'
            }
        
        if not token.is_valid():
            return {
                'success': False,
                'error': 'Token ist abgelaufen oder wurde bereits verwendet.'
            }
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        # Verify user email
        user = token.user
        user.is_verified = True
        user.save()
        
        return {
            'success': True,
            'user_id': str(user.id),
            'email': user.email
        }
    
    def _render_html_response(self, success, title, message, details=""):
        """Render HTML response for browser"""
        from django.http import HttpResponse
        
        color = "#4CAF50" if success else "#f44336"
        icon = "✅" if success else "❌"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - Auth Service</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, {'#667eea 0%, #764ba2 100%' if success else '#f093fb 0%, #f5576c 100%'});
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 50px 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                    width: 100%;
                    animation: slideIn 0.5s ease-out;
                }}
                @keyframes slideIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(-20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                .icon {{
                    font-size: 80px;
                    margin-bottom: 20px;
                    animation: bounce 1s ease-in-out;
                }}
                @keyframes bounce {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                }}
                h1 {{
                    color: {color};
                    font-size: 32px;
                    margin-bottom: 20px;
                    font-weight: 700;
                }}
                .message {{
                    font-size: 20px;
                    color: #333;
                    margin-bottom: 15px;
                    line-height: 1.6;
                }}
                .details {{
                    font-size: 16px;
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 40px;
                    background: {color};
                    color: white;
                    text-decoration: none;
                    border-radius: 50px;
                    font-size: 18px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }}
                .button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #999;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">{icon}</div>
                <h1>{title}</h1>
                <div class="message">{message}</div>
                <div class="details">{details}</div>
                <a href="/" class="button">Zur Startseite</a>
                <div class="footer">
                    © 2025 PalmDynamicX Auth Service
                </div>
            </div>
        </body>
        </html>
        """
        
        status_code = 200 if success else 400
        return HttpResponse(html, status=status_code, content_type='text/html')


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
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Passwort-Reset-Token aus der E-Mail (für GET)',
        ),
    ],
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
    description='Setzt das Passwort zurück mit einem Token. Unterstützt GET (zeigt Formular) und POST (setzt Passwort zurück).'
)
class ResetPasswordView(APIView):
    """
    Reset password with token.
    
    GET /api/accounts/reset-password/?token=reset_token (zeigt HTML-Formular)
    POST /api/accounts/reset-password/ (für API-Calls)
    Body: {
        "token": "reset_token",
        "new_password": "NewPassword123!",
        "new_password2": "NewPassword123!"
    }
    """
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        """Show password reset form"""
        from django.http import HttpResponse
        
        token = request.GET.get('token', '')
        
        # Validate token exists and is valid
        token_valid = False
        error_message = ""
        
        if token:
            try:
                token_obj = PasswordResetToken.objects.get(token=token)
                if token_obj.is_valid():
                    token_valid = True
                else:
                    error_message = "Der Link ist abgelaufen oder wurde bereits verwendet."
            except PasswordResetToken.DoesNotExist:
                error_message = "Ungültiger Link."
        else:
            error_message = "Kein Token gefunden."
        
        if not token_valid:
            return self._render_error_html(error_message)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Passwort zurücksetzen - Auth Service</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 500px;
                    width: 100%;
                    animation: slideIn 0.5s ease-out;
                }}
                @keyframes slideIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(-20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                h1 {{
                    color: #f5576c;
                    font-size: 32px;
                    margin-bottom: 10px;
                    font-weight: 700;
                    text-align: center;
                }}
                .subtitle {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 16px;
                }}
                .form-group {{
                    margin-bottom: 25px;
                }}
                label {{
                    display: block;
                    margin-bottom: 8px;
                    color: #333;
                    font-weight: 600;
                    font-size: 14px;
                }}
                input[type="password"] {{
                    width: 100%;
                    padding: 15px;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    font-size: 16px;
                    transition: all 0.3s ease;
                }}
                input[type="password"]:focus {{
                    outline: none;
                    border-color: #f5576c;
                    box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.1);
                }}
                button {{
                    width: 100%;
                    padding: 15px;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
                }}
                button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
                }}
                button:active {{
                    transform: translateY(0);
                }}
                button:disabled {{
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                }}
                .message {{
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    display: none;
                }}
                .message.success {{
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                    display: block;
                }}
                .message.error {{
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                    display: block;
                }}
                .password-requirements {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    font-size: 13px;
                }}
                .password-requirements ul {{
                    margin: 10px 0 0 20px;
                    color: #666;
                }}
                .password-requirements li {{
                    margin: 5px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    color: #999;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Passwort zurücksetzen</h1>
                <div class="subtitle">Gib dein neues Passwort ein</div>
                
                <div id="message" class="message"></div>
                
                <div class="password-requirements">
                    <strong>Passwort-Anforderungen:</strong>
                    <ul>
                        <li>Mindestens 8 Zeichen</li>
                        <li>Nicht zu ähnlich zu deinen anderen Informationen</li>
                        <li>Nicht ausschließlich numerisch</li>
                    </ul>
                </div>
                
                <form id="resetForm">
                    <div class="form-group">
                        <label for="password">Neues Passwort</label>
                        <input 
                            type="password" 
                            id="password" 
                            name="new_password"
                            required 
                            minlength="8"
                            placeholder="Mindestens 8 Zeichen"
                        >
                    </div>
                    
                    <div class="form-group">
                        <label for="confirmPassword">Passwort bestätigen</label>
                        <input 
                            type="password" 
                            id="confirmPassword" 
                            name="new_password2"
                            required
                            placeholder="Passwort wiederholen"
                        >
                    </div>
                    
                    <button type="submit" id="submitBtn">Passwort zurücksetzen</button>
                </form>
                
                <div class="footer">
                    © 2025 PalmDynamicX Auth Service
                </div>
            </div>
            
            <script>
                const form = document.getElementById('resetForm');
                const submitBtn = document.getElementById('submitBtn');
                const messageDiv = document.getElementById('message');
                const token = '{token}';
                
                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    
                    const password = document.getElementById('password').value;
                    const confirmPassword = document.getElementById('confirmPassword').value;
                    
                    // Reset message
                    messageDiv.className = 'message';
                    messageDiv.textContent = '';
                    
                    // Validate passwords match
                    if (password !== confirmPassword) {{
                        showMessage('error', '❌ Passwörter stimmen nicht überein');
                        return;
                    }}
                    
                    // Disable button and show loading
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Wird verarbeitet...';
                    
                    try {{
                        const response = await fetch(window.location.pathname, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                token: token,
                                new_password: password,
                                new_password2: confirmPassword
                            }})
                        }});
                        
                        const data = await response.json();
                        
                        if (response.ok) {{
                            showMessage('success', '✅ Passwort erfolgreich geändert! Weiterleitung...');
                            form.style.display = 'none';
                            
                            // Redirect to home after 2 seconds
                            setTimeout(() => {{
                                window.location.href = '/';
                            }}, 2000);
                        }} else {{
                            // Handle validation errors
                            let errorMsg = '❌ ';
                            if (data.error) {{
                                errorMsg += data.error;
                            }} else if (data.new_password) {{
                                errorMsg += data.new_password.join(' ');
                            }} else if (data.new_password2) {{
                                errorMsg += data.new_password2.join(' ');
                            }} else {{
                                errorMsg += 'Fehler beim Zurücksetzen des Passworts';
                            }}
                            showMessage('error', errorMsg);
                            submitBtn.disabled = false;
                            submitBtn.textContent = 'Passwort zurücksetzen';
                        }}
                    }} catch (error) {{
                        showMessage('error', '❌ Netzwerkfehler. Bitte versuche es erneut.');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Passwort zurücksetzen';
                    }}
                }});
                
                function showMessage(type, text) {{
                    messageDiv.className = `message ${{type}}`;
                    messageDiv.textContent = text;
                }}
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html, content_type='text/html')
    
    def _render_error_html(self, error_message):
        """Render error page"""
        from django.http import HttpResponse
        
        html = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fehler - Auth Service</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    padding: 50px 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                    width: 100%;
                }}
                .icon {{
                    font-size: 80px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #f44336;
                    font-size: 32px;
                    margin-bottom: 20px;
                    font-weight: 700;
                }}
                .message {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                    line-height: 1.6;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 40px;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 50px;
                    font-size: 18px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }}
                .button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">❌</div>
                <h1>Link ungültig</h1>
                <div class="message">{error_message}</div>
                <a href="/" class="button">Zur Startseite</a>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html, status=400, content_type='text/html')
    
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
