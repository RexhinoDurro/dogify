# server/server/settings.py - Enhanced settings with bot middleware integration
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

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
    
    # Enhanced Bot Detection Middleware (serves HTML to bots, redirects humans)
    'bot_detection.enhanced_bot_middleware.EnhancedBotHTMLMiddleware',
    
    # Basic Protection Middleware (API protection only)
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

# Database - Using SQLite3 for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Simple cache using database (no Redis needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'bot_detection_cache',
    }
}

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

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # For testing
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}

# CORS settings - Updated for enhanced middleware
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Main React app
    "http://127.0.0.1:5173",
    "http://localhost:3001",  # Bot detection React app  
    "http://127.0.0.1:3001",
]

CORS_ALLOW_CREDENTIALS = True

# Enhanced CORS handling
CORS_ALLOW_ALL_ORIGINS = False  # Keep this False for security
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
    'x-bot-detection',  # Custom header for bot detection
    'x-fingerprint',    # Custom header for fingerprinting
]

# Enhanced Bot Detection Settings
BOT_DETECTION_SETTINGS = {
    'ENABLE_BOT_BLOCKING': True,
    'ENABLE_HTML_SERVING': True,  # NEW: Enable HTML serving to bots
    'STRICT_MODE': os.environ.get('BOT_DETECTION_STRICT', 'False').lower() == 'true',
    'MAIN_SITE_URL': os.environ.get('MAIN_SITE_URL', 'http://localhost:5173'),
    'BOT_SITE_URL': os.environ.get('BOT_SITE_URL', 'http://localhost:3001'),
    'REDIRECT_DELAY': 2,  # seconds
    'AUTO_BLACKLIST_THRESHOLD': 0.8,
    'RATE_LIMIT_PER_MINUTE': 100,
    'FACEBOOK_BOT_DETECTION': True,
    'SERVE_HTML_TO_BOTS': True,  # NEW: Serve static HTML to bots
    'HTML_CACHE_DURATION': 3600,  # Cache HTML responses for 1 hour
}

# Admin API Key for management endpoints
ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', 'dogify_admin_2025_change_me')

# Threat Intelligence Settings
THREAT_INTEL_WEBHOOK_SECRET = os.environ.get('THREAT_INTEL_SECRET', 'webhook_secret_change_me')

# Enhanced Logging with bot detection focus
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
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'bot_detection.log',
            'formatter': 'verbose',
        },
        'bot_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'bot_visits.log',
            'formatter': 'simple',
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
        'bot_visits': {
            'handlers': ['console', 'bot_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create required directories
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(BASE_DIR / 'static', exist_ok=True)
os.makedirs(BASE_DIR / 'ml_models', exist_ok=True)

# Security Headers for enhanced protection
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Additional Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True