"""Settings that need to be set in order to run the tests."""
import os

DEBUG = True

SITE_ID = 1

AUTH_USER_MODEL = 'auth.User'

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

PAYPAL_API_URL = 'https://api.sandbox.paypal.com/nvp'

PAYPAL_LOGIN_URL = (
    'https://www.sandbox.paypal.com/cgi-bin/'
    'webscr?cmd=_express-checkout&token='
)

# [OPTIONAL]
# The general description of all Sales (not the one of a single item!)
SALE_DESCRIPTION = 'Your payment to {0}'.format(HOSTNAME)


# Settings for local_settings.py
PAYPAL_USER = 'api_user@example.com'
PAYPAL_PWD = 'your api password'
PAYPAL_SIGNATURE = 'your api signature'
