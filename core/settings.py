import os
from pathlib import Path
from os import getenv
from dotenv import load_dotenv
import django.db.backends.postgresql

# Load environment variables from .env.local if it exists, otherwise from .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'a-default-secret-key-for-local-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

CSRF_TRUSTED_ORIGINS = ['https://kbdiploo.pythonanywhere.com', 'http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost', 'http://127.0.0.1']

CORS_ALLOWED_ORIGINS = ['https://kbdiploo.pythonanywhere.com', 'http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost', 'http://127.0.0.1']

ALLOWED_HOSTS = ['kbdiploo.pythonanywhere.com', '127.0.0.1', 'localhost', '.pythonanywhere.com']

AUTH_USER_MODEL = 'account.Account'
LOGIN_URL = 'account:login'
LOGOUT_REDIRECT_URL = '/'

SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'


INSTALLED_APPS = [
    'account',
    'main',
    'mpesa',
    'sweetify',
    'corsheaders',
    'bootstrap_modal_forms',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

# Email Configuration for Password Reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tingzlarry@gmail.com' 
EMAIL_HOST_PASSWORD ='xkuh apzw awtn inyf' 
DEFAULT_FROM_EMAIL = 'Denkam Waters <noreply@denkamwaters.com>'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database configuration with timezone support
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'denkam_waters'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,  # Reuse connections for 60 seconds
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
        'OPTIONS': {
            'options': '-c timezone=utc',
        },
    }
}

# Enable timezone support
USE_TZ = True
TIME_ZONE = 'UTC'

# No custom routers needed for local development
DATABASE_ROUTERS = []


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


LANGUAGE_CODE = 'en-us'



USE_I18N = True

USE_TZ = True


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main', 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



# Email Configuration for Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# M-Pesa Configuration
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
MPESA_API_ENVIRONMENT = 'sandbox' # Default to sandbox

if MPESA_API_ENVIRONMENT == 'live':
    MPESA_API_URL = 'https://api.safaricom.co.ke'
else:
    MPESA_API_URL = 'https://sandbox.safaricom.co.ke'

MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://your-domain.com/mpesa/callback/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


# CSRF Settings
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_SAMESITE = 'Lax'

# Session Settings
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SAMESITE = 'Lax'

# M-Pesa Configuration
MPESA_ENVIRONMENT = 'sandbox'  # 'sandbox' or 'production'
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', 'your_sandbox_consumer_key')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'your_sandbox_consumer_secret')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', 'your_sandbox_passkey')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')  # Sandbox shortcode
MPESA_INITIATOR_USERNAME = os.getenv('MPESA_INITIATOR_USERNAME', 'testapi')
MPESA_INITIATOR_PASSWORD = os.getenv('MPESA_INITIATOR_PASSWORD', '')
MPESA_API_URL = 'https://sandbox.safaricom.co.ke' if MPESA_ENVIRONMENT == 'sandbox' else 'https://api.safaricom.co.ke'
MPESA_CALLBACK_URL = getenv('MPESA_CALLBACK_URL', 'https://your-domain.com/mpesa/callback/')
MPESA_ACCOUNT_REFERENCE = 'WATER_BILL'
MPESA_TRANSACTION_DESC = 'Payment for water bill'