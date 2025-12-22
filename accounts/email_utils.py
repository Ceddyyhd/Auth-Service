"""
Email utility functions for sending various emails.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_verification_email(user, token):
    """
    Send email verification email to user.
    """
    verification_url = f"{settings.EMAIL_VERIFY_URL}?token={token}"
    
    subject = 'Bestätige deine E-Mail-Adresse'
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; }}
            .button {{ display: inline-block; padding: 12px 30px; background-color: #4CAF50; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✉️ E-Mail Bestätigung</h1>
            </div>
            <div class="content">
                <h2>Hallo {user.get_full_name() or user.username}!</h2>
                <p>Vielen Dank für deine Registrierung. Bitte bestätige deine E-Mail-Adresse, 
                   um dein Konto zu aktivieren.</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">E-Mail bestätigen</a>
                </p>
                <p>Oder kopiere diesen Link in deinen Browser:</p>
                <p style="word-break: break-all; color: #666; font-size: 14px;">
                    {verification_url}
                </p>
                <p><strong>Dieser Link ist 24 Stunden gültig.</strong></p>
                <p>Wenn du dich nicht registriert hast, ignoriere diese E-Mail.</p>
            </div>
            <div class="footer">
                <p>© 2024 Auth Service. Alle Rechte vorbehalten.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """
    Send password reset email to user.
    """
    reset_url = f"{settings.PASSWORD_RESET_URL}?token={token}"
    
    subject = 'Passwort zurücksetzen'
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #FF5722; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; }}
            .button {{ display: inline-block; padding: 12px 30px; background-color: #FF5722; 
                      color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Passwort zurücksetzen</h1>
            </div>
            <div class="content">
                <h2>Hallo {user.get_full_name() or user.username}!</h2>
                <p>Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Passwort zurücksetzen</a>
                </p>
                <p>Oder kopiere diesen Link in deinen Browser:</p>
                <p style="word-break: break-all; color: #666; font-size: 14px;">
                    {reset_url}
                </p>
                <div class="warning">
                    <strong>⚠️ Wichtig:</strong>
                    <ul>
                        <li>Dieser Link ist nur 1 Stunde gültig</li>
                        <li>Der Link kann nur einmal verwendet werden</li>
                        <li>Wenn du diese Anfrage nicht gestellt hast, ignoriere diese E-Mail</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>© 2024 Auth Service. Alle Rechte vorbehalten.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_test_email(recipient_email):
    """
    Send a test email to verify SMTP configuration.
    """
    subject = 'Test E-Mail - SMTP Konfiguration'
    
    html_message = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #2196F3; color: white; padding: 20px; text-align: center; }
            .content { background-color: #f9f9f9; padding: 30px; }
            .success { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ SMTP Test erfolgreich</h1>
            </div>
            <div class="content">
                <div class="success">
                    <strong>Glückwunsch!</strong> Deine SMTP-Konfiguration funktioniert einwandfrei.
                </div>
                <p>Diese Test-E-Mail wurde erfolgreich über deine konfigurierten SMTP-Einstellungen versendet.</p>
                <p><strong>E-Mail-Details:</strong></p>
                <ul>
                    <li>Empfänger: """ + recipient_email + """</li>
                    <li>Server: """ + settings.EMAIL_HOST + """</li>
                    <li>Port: """ + str(settings.EMAIL_PORT) + """</li>
                    <li>TLS: """ + ("Ja" if settings.EMAIL_USE_TLS else "Nein") + """</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_changed_notification(user):
    """
    Send notification email when password is changed successfully.
    """
    subject = 'Dein Passwort wurde geändert'
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 30px; }}
            .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Passwort geändert</h1>
            </div>
            <div class="content">
                <h2>Hallo {user.get_full_name() or user.username}!</h2>
                <p>Dein Passwort wurde erfolgreich geändert.</p>
                <div class="warning">
                    <strong>⚠️ Wichtig:</strong>
                    <p>Wenn du diese Änderung nicht vorgenommen hast, kontaktiere sofort den Support!</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
