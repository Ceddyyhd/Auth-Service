"""
Django settings for auth_service project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,auth.palmdynamicx.de,www.auth.palmdynamicx.de'
).split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'oauth2_provider',
    'corsheaders',
    'drf_spectacular',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.microsoft',
    'allauth.socialaccount.providers.apple',
    
    # Local apps
    'accounts',
    'permissions_system',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'auth_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'auth_service.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# OAuth2 Settings
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'profile': 'Access to profile information',
        'email': 'Access to email address',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': config('OAUTH2_ACCESS_TOKEN_EXPIRE_SECONDS', default=3600, cast=int),
    'REFRESH_TOKEN_EXPIRE_SECONDS': config('OAUTH2_REFRESH_TOKEN_EXPIRE_SECONDS', default=86400, cast=int),
    'ROTATE_REFRESH_TOKEN': True,
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
}

# CORS Settings - Sichere Cross-Origin-Anfragen
# Tragen Sie hier alle Domains ein, die auf die API zugreifen dürfen
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8080,https://palmdynamicx.de,https://www.palmdynamicx.de'
).split(',')

# WICHTIG: In Produktion NUR vertrauenswürdige Domains hinzufügen!
# Niemals CORS_ALLOW_ALL_ORIGINS = True in Produktion!
CORS_ALLOW_CREDENTIALS = True  # Erlaubt Cookies und Authorization-Header

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Cache Settings (Redis) - Optional
# Wenn Redis nicht verfügbar, wird Default-Cache verwendet
try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
except ImportError:
    # Fallback zu DB-basiertem Cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session Settings for SSO
SESSION_COOKIE_AGE = 604800  # 7 days in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cookies in cross-site requests (important for SSO)
# In production with HTTPS:
# SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
# SESSION_COOKIE_DOMAIN = '.yourdomain.com'  # Share cookie across subdomains

# SSO Configuration
SSO_TOKEN_EXPIRY_MINUTES = 5  # SSO tokens valid for 5 minutes
SSO_SESSION_DURATION_DAYS = 7  # SSO sessions last 7 days

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)  # Für Port 465
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')
SERVER_EMAIL = config('SERVER_EMAIL', default=config('DEFAULT_FROM_EMAIL', default='noreply@example.com'))

# Email URLs für Verification und Password Reset
EMAIL_VERIFY_URL = config('EMAIL_VERIFY_URL', default='http://localhost:3000/verify-email')
PASSWORD_RESET_URL = config('PASSWORD_RESET_URL', default='http://localhost:3000/reset-password')

# Email Token Expiry
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = config('EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS', default=24, cast=int)
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = config('PASSWORD_RESET_TOKEN_EXPIRY_HOURS', default=1, cast=int)

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Produktions-Sicherheitseinstellungen (über .env steuerbar)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Für Nginx/Reverse Proxy
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# CSRF Trusted Origins (für POST-Requests von anderen Domains)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://auth.palmdynamicx.de,https://palmdynamicx.de,https://www.palmdynamicx.de'
).split(',')

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'PalmDynamicX Auth Service API',
    'DESCRIPTION': '''Zentraler Authentifizierungs- und Autorisierungsservice für PalmDynamicX
    
    ## 🔒 Sicherheit
    - Alle Anfragen müssen über HTTPS erfolgen (in Produktion)
    - JWT-Tokens für Authentifizierung
    - bcrypt Password-Hashing
    - Rate Limiting aktiviert
    - CORS konfiguriert für sichere Cross-Origin-Anfragen
    
    ## 🔑 Authentifizierung
    Fügen Sie den Access-Token im Authorization-Header hinzu:
    ```
    Authorization: Bearer <ACCESS_TOKEN>
    ```
    
    ## 📚 Weitere Dokumentation
    - [Vollständige API-Referenz](https://github.com/PalmDynamicX/Auth-Service/blob/main/API_REFERENCE.md)
    - [Sicherheits-Guide](https://github.com/PalmDynamicX/Auth-Service/blob/main/SECURITY.md)
    - [Integration Guide](https://github.com/PalmDynamicX/Auth-Service/blob/main/WEBSITE_INTEGRATION.md)
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    'SERVERS': [
        {'url': 'https://auth.palmdynamicx.de', 'description': 'Produktions-Server'},
        {'url': 'http://localhost:8000', 'description': 'Lokale Entwicklung'},
    ],
    'SECURITY': [
        {'Bearer': []}
    ],
    'COMPONENTS': {
        'securitySchemes': {
            'Bearer': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'JWT Access Token (Gültigkeitsdauer: 15 Minuten)'
            }
        }
    },
}

# Django Allauth Settings
AUTHENTICATION_BACKENDS = [
    'accounts.admin_mfa.AdminMFABackend',  # Custom MFA backend for admin
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Social Account Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'APP': {
            'client_id': config('FACEBOOK_APP_ID', default=''),
            'secret': config('FACEBOOK_APP_SECRET', default=''),
            'key': ''
        },
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'picture',
        ],
    },
    'github': {
        'APP': {
            'client_id': config('GITHUB_CLIENT_ID', default=''),
            'secret': config('GITHUB_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'user',
            'user:email',
        ],
    },
    'microsoft': {
        'APP': {
            'client_id': config('MICROSOFT_CLIENT_ID', default=''),
            'secret': config('MICROSOFT_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'User.Read',
        ],
    },
    'apple': {
        'APP': {
            'client_id': config('APPLE_CLIENT_ID', default=''),
            'secret': config('APPLE_CLIENT_SECRET', default=''),
            'key': config('APPLE_KEY_ID', default=''),
            'certificate_key': config('APPLE_PRIVATE_KEY', default=''),
        },
        'SCOPE': ['name', 'email'],
    },
}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# ===========================
# EMAIL CONFIGURATION
# ===========================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
SERVER_EMAIL = config('SERVER_EMAIL', default=EMAIL_HOST_USER)

# Email verification settings
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = 1

# Frontend URLs for email links
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
EMAIL_VERIFY_URL = f"{FRONTEND_URL}/verify-email"
PASSWORD_RESET_URL = f"{FRONTEND_URL}/reset-password"
