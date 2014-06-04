import os
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'predictions',                      # Or path to database file if using sqlite3.
        'USER': 'predictions',                      # Not used with sqlite3.
        'PASSWORD': os.environ.get('PREDICTIONS_DB_PROD_PASS'),                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
