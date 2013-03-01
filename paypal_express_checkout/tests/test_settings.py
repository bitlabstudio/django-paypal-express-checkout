"""Settings that need to be set in order to run the tests."""
import os

DEBUG = True

SITE_ID = 1

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = 'paypal_express_checkout.tests.urls'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(__file__, '../../../static/')

STATICFILES_DIRS = (
    os.path.join(__file__, 'test_static'),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates'),
)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), 'coverage')

COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions', '__init__',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_libs',
]

INTERNAL_APPS = [
    'django_nose',
    'paypal_express_checkout',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

# this leads to the dummy home page added for testing purposes.
LOGIN_URL = '/'


# ======================
# necessary app settings
# ======================
HOSTNAME = 'http://localhost:8000'  # without trailing slash

API_PAYPAL = 'https://api.sandbox.paypal.com/nvp'

LOGIN_PAYPAL = (
    'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token='  # NOQA
)

# [OPTIONAL]
# If set, this is set to a string representing a model and its field,
# where the paid amount should be added to. E.g.: 'UserProfile.account_balance'
# ADD_TO_FIELD = ''

# If the user should be able to set an amount for the bought item.
# If False, the amount defaults to 1
SET_QUANTITY = True

# Define what should be displayed in case of SET_QUANTITY is True.
# Is not used, when SET_QUANTITY is False.
# Must be a tuple with ('singular', 'plural').
# e.g. ('year', 'years')
QUANTITY_NAME = ('piece', 'pieces')

# [OPTIONAL]
# The general description of all Sales (not the one of a single item!)
SALE_DESCRIPTION = 'Your payment to {0}'.format(HOSTNAME)


# Settings for local_settings.py
API_USER = 'api_user@example.com'
API_PASSWORD = 'your api password'
API_SIGNATURE = 'your api signature'
