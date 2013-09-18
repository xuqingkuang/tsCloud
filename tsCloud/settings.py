import sys, os

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

PROJECT_NAME = 'tsCloud'
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# Add git sub modules into sys path.
GIT_SUB_MODULES = os.path.join(PROJECT_DIR, '../submodules') #Relative paths ok too

for folder in os.listdir(GIT_SUB_MODULES):
    path = os.path.join(GIT_SUB_MODULES, folder)
    if not path in sys.path:
        sys.path.append(path)

# Django settings for tsCloud project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Xuqing Kuang', 'kuangxq@thundersoft.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',                       # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/tsCloud_cache',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.normpath(os.path.join(PROJECT_DIR, '../media'))
# ADMIN_MEDIA_ROOT = os.path.join(PROJECT_DIR, 'admin-media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.normpath(os.path.join(PROJECT_DIR, '../static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qx&amp;%0zjxy2h5k52k(*zoi#d4@)ms-^x+xgqf#(e918)@l_8v#5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'tsCloud.ctauth.middleware.CTUserTokenMiddleware',
)

ROOT_URLCONF = 'tsCloud.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'tsCloud.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django_mptt_admin',
    'tsCloud.core',
    # 'tsCloud.ctauth',
    'tsCloud.ad',
    # 'tsCloud.diary',
    'tsCloud.photo',
    'tsCloud.ucam',
    'tsCloud.resource'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# tsCloud specific settings


# wadofstuff serializer settings
# http://code.google.com/p/wadofstuff/wiki/DjangoFullSerializers
SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json',
}

SINA_APP_KEY = '2539482304'
SINA_APP_SECRET = '9ae7476217ee243bd78857194556a7a6'

QINIU_STORAGE_KEY = 'sVQPt9QfybbJPvYN5dqcTGp9k7ya37yvie7as7rv'
QINIU_STORAGE_SECRET = 'm33C5JmFZ9qFAt-vmjSgje-AIuSnzVKpBuR1SCKZ'

SHORT_URL_SERVICE = 'http://api.x.co/Squeeze.svc/text/69b263c1e0de4257925bd6772c090295?url=%s'

UPLOAD_DIR = 'photo/'
UPLOAD_ROOT = os.path.join(MEDIA_ROOT, UPLOAD_DIR)
UPLOAD_URL = os.path.join(MEDIA_URL, UPLOAD_ROOT)

RESIZE_QUALITY = 85
