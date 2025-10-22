# matriz/settings.py

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

# Lee la SECRET_KEY desde las variables de entorno. ¡Mucho más seguro!
SECRET_KEY = config('SECRET_KEY')

# DEBUG debe ser False en producción. Se controla con una variable de entorno.
DEBUG = config('DEBUG', default=False, cast=bool)

# Configura los hosts permitidos desde una variable de entorno.
# Ejemplo: ALLOWED_HOSTS="miapp.railway.app,www.miapp.com"
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,healthcheck.railway.app').split(',')

# Agregar hosts adicionales para Railway
ALLOWED_HOSTS += [
    'healthcheck.railway.app',  # Para healthchecks de Railway
    '.railway.app',  # Para cualquier subdominio de railway.app
]

# Permitir 0.0.0.0 en desarrollo (útil para previews/local bind)
if DEBUG and '0.0.0.0' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('0.0.0.0')

# CSRF: dominios confiables para solicitudes desde Railway (usar esquema https)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app,https://healthcheck.railway.app'
).split(',')

# Cookies seguras en producción
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Añade esto
    'django.contrib.staticfiles',
    'gestion_riesgos',
    'cumplimiento',
    'agenda',
    'accidentes', # Mueve tu app aquí
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Configuración de WhiteNoise
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Esto parece estar mal en tu config original, lo corregimos
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
# Siempre usar PostgreSQL desde variable de entorno DATABASE_URL. No usar SQLite.
DATABASE_URL_VALUE = config('DATABASE_URL', default='')
if not DATABASE_URL_VALUE:
    raise ValueError("DATABASE_URL no está definido en el entorno.")

# Importante: usar parse() con el valor leído del .env para no depender de os.environ
_db_config = dj_database_url.parse(DATABASE_URL_VALUE, conn_max_age=600, ssl_require=not DEBUG)
if not _db_config:
    raise ValueError("DATABASE_URL es inválido o no pudo parsearse.")

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
LANGUAGE_CODE = 'es-cl' # Cambiado a español de Chile
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Configuración de WhiteNoise para servir archivos estáticos eficientemente
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'