import os
from pathlib import Path
from decouple import AutoConfig, Config, RepositoryEnv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Carga de variables de entorno (.env local o variables de Railway)
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    config = Config(RepositoryEnv(str(ENV_FILE)))
else:
    config = AutoConfig(search_path=BASE_DIR)

# 2. Seguridad
# En local leerá 'tu_clave_secreta_local...' del .env, en prod usará la variable de Railway
SECRET_KEY = config('SECRET_KEY', default='insecure-secret-key-change-me')

# DEBUG será True si está en tu .env local, False por defecto en producción
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,healthcheck.railway.app').split(',')
ALLOWED_HOSTS += [
    'healthcheck.railway.app',
    '.railway.app',
    '.up.railway.app',
]

if DEBUG and '0.0.0.0' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('0.0.0.0')

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app,https://*.up.railway.app,https://healthcheck.railway.app'
).split(',')

# 3. Configuración HTTPS/Seguridad (Se activa solo si DEBUG=False)
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_REDIRECT_EXEMPT = [r'^healthz/?$']

# 4. Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    'gestion_riesgos',
    'cumplimiento',
    'agenda',
    'accidentes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'matriz.wsgi.application'

# 5. Base de Datos (Conexión Universal)
DATABASE_URL_VALUE = config('DATABASE_URL', default=None)

if DATABASE_URL_VALUE:
    _db_config = dj_database_url.parse(
        DATABASE_URL_VALUE,
        conn_max_age=600,
        # TRUCO: Permitimos SSL siempre si estamos conectando a Railway, 
        # incluso en local, para evitar rechazos de conexión.
        ssl_require=True 
    )
else:
    _db_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

DATABASES = {
    'default': _db_config
}

# 6. Validadores de Password
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 7. Internacionalización
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 8. Archivos Estáticos
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Directorios adicionales donde Django buscará archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / "gestion_riesgos" / "static",
]

# WhiteNoise para servir archivos estáticos
# En desarrollo (DEBUG=True), usar el storage por defecto de Django
# En producción (DEBUG=False), usar WhiteNoise con compresión
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'