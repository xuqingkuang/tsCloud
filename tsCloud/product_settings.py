from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tsCloud',                       # Or path to database file if using sqlite3.
        'USER': 'tsCloud',                       # Not used with sqlite3.
        'PASSWORD': 'abc123',                    # Not used with sqlite3.
        'HOST': 'localhost',                     # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
