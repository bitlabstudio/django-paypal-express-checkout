import os
from setuptools import setup, find_packages
import paypal_express_checkout


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-paypal-express-checkout",
    version=paypal_express_checkout.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, url, paypal, paypal_express_checkout, API',
    author='Daniel Kaufhold',
    author_email='daniel.kaufhold@bitmazk.com',
    url="https://github.com/bitmazk/django-paypal-express-checkout",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
        'django_libs',
    ],
    tests_require=[
        'fabric',
        'factory_boy',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
        'flake8',
        'django-libs'
    ],
    test_suite='paypal_express_checkout.tests.runtests.runtests',
)
