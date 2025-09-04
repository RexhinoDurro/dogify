# server/server/settings.py - Simplified PostgreSQL settings (no decouple)
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists
def load_env_file():
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)

# Load environment variables from .env file
load_env_file()

# Helper function for environment variables
def get_env_bool(key, default=False):
    """Get environment variable as boolean"""
    value = os.environ.get(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_list(key, default=''):
    """Get environment variable as list (comma-separated)"""
    value = os.environ.get(key, default)
    return [item.strip() for item in value.split(',') if item.strip()]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_bool('DEBUG', False)

ALLOWED_HOSTS = get_env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'corsheaders',
    'rest_framework',
    
    # Local apps
    'bot_detection',
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
    
    # Enhanced Bot Detection Middleware
    'bot_detection.enhanced_bot_middleware.EnhancedBotHTMLMiddleware',
    'bot_detection.middleware.BotProtectionMiddleware',
]

ROOT_URLCONF = 'server.urls'

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

WSGI_APPLICATION = 'server.wsgi.application'

# Database Configuration - PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'dogify_bot_detection'),
        'USER': os.environ.get('DB_USER', 'dogify_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password_here'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}

# Cache Configuration - Database-based caching only
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'bot_detection_cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 5000,  # Increased for better performance
            'CULL_FREQUENCY': 3,
        }
    }
}

# Session Configuration - Database-based sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# Media files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '200/hour',  # Increased for production
    }
}

# CORS settings
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')
if CORS_ORIGINS:
    CORS_ALLOWED_ORIGINS = get_env_list('CORS_ORIGINS')
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-bot-detection',
    'x-fingerprint',
]

# Bot Detection Settings
BOT_DETECTION_SETTINGS = {
    'ENABLE_BOT_BLOCKING': get_env_bool('BOT_BLOCKING_ENABLED', True),
    'ENABLE_HTML_SERVING': get_env_bool('HTML_SERVING_ENABLED', True),
    'STRICT_MODE': get_env_bool('BOT_DETECTION_STRICT', False),
    'MAIN_SITE_URL': os.environ.get('MAIN_SITE_URL', 'http://localhost:5173'),
    'BOT_SITE_URL': os.environ.get('BOT_SITE_URL', 'http://localhost:3001'),
    'REDIRECT_DELAY': int(os.environ.get('REDIRECT_DELAY', 2)),
    'AUTO_BLACKLIST_THRESHOLD': float(os.environ.get('AUTO_BLACKLIST_THRESHOLD', 0.8)),
    'RATE_LIMIT_PER_MINUTE': int(os.environ.get('RATE_LIMIT_PER_MINUTE', 100)),
    'FACEBOOK_BOT_DETECTION': True,
    'SERVE_HTML_TO_BOTS': True,
    'HTML_CACHE_DURATION': 3600,
}

# Admin API Key
ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', 'dogify_admin_2025_change_me')
THREAT_INTEL_WEBHOOK_SECRET = os.environ.get('THREAT_INTEL_SECRET', 'webhook_secret_change_me')

# Enhanced Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'bot_detection.log',
            'maxBytes': 10*1024*1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'bot_detection': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
    },
}

# Create directories
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'static', exist_ok=True)
os.makedirs(BASE_DIR / 'ml_models', exist_ok=True)
os.makedirs(BASE_DIR / 'media', exist_ok=True)

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Production Security Settings
if not DEBUG:
    # SSL/HTTPS Settings
    SECURE_SSL_REDIRECT = get_env_bool('FORCE_SSL', True)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Additional security
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Use WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
