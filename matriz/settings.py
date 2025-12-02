import os
from pathlib import Path
from decouple import AutoConfig, Config, RepositoryEnv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env en la raíz del proyecto, de forma explícita
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    config = Config(RepositoryEnv(str(ENV_FILE)))
else:
    config = AutoConfig(search_path=BASE_DIR)

# Lee la SECRET_KEY desde las variables de entorno.
SECRET_KEY = config('SECRET_KEY', default='insecure-secret-key-change-me')

# DEBUG debe ser False en producción.
DEBUG = config('DEBUG', default=False, cast=bool)

# Configura los hosts permitidos desde una variable de entorno.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,healthcheck.railway.app').split(',')

# Agregar hosts adicionales para Railway
ALLOWED_HOSTS += [
    'healthcheck.railway.app',  # Para healthchecks de Railway
    '.railway.app',             # Subdominios antiguos de railway.app
    '.up.railway.app',          # Subdominios nuevos de up.railway.app
]

# Permitir 0.0.0.0 en desarrollo (útil para previews/local bind)
if DEBUG and '0.0.0.0' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('0.0.0.0')

# CSRF: dominios confiables para solicitudes desde Railway
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app,https://*.up.railway.app,https://healthcheck.railway.app'
).split(',')

# Cookies seguras en producción
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

# Respetar el proxy de Railway para detectar HTTPS correctamente
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Evitar redirecciones para healthcheck y conservar barra opcional
SECURE_REDIRECT_EXEMPT = [r'^healthz/?$']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # WhiteNoise antes de staticfiles
    'django.contrib.staticfiles',
    'gestion_riesgos',
    'cumplimiento',
    'agenda',
    'accidentes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Middleware de WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'matriz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'matriz.wsgi.application'


# Database
# Usar PostgreSQL desde DATABASE_URL cuando esté definido. Si no, fallback a SQLite
DATABASE_URL_VALUE = config('DATABASE_URL', default=None)

if DATABASE_URL_VALUE:
    _db_config = dj_database_url.parse(
        DATABASE_URL_VALUE,
        conn_max_age=600,
        ssl_require=not DEBUG  # Requiere SSL si no estamos en DEBUG
    )
else:
    _db_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

DATABASES = {
    'default': _db_config
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Configuración de WhiteNoise (CORREGIDA PARA EVITAR ERRORES DE DESPLIEGUE)
# Se usa CompressedStaticFilesStorage en lugar de ManifestStaticFilesStorage
# para evitar fallos si faltan archivos referenciados.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'