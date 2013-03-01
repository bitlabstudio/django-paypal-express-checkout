Django Paypal Express Checkout
==============================

A Django application to integrate PayPal in your Django driven site.

Features
--------

Currently it only features a simple express checkout implementation for one
item or to allow a user to raise his account balance.

So if you e.g. have yearly payment for an account or only one item on sale,
this app is capable of doing the PayPal express checkout handling for you.

Check the "Installation" section on what you are yet able to set up.


Installation
------------

You need to install the following prerequisites in order to use this app::

    pip install Django

If you want to install the latest stable release from PyPi::

    $ pip install django-paypal-express-checkout

If you feel adventurous and want to install the latest commit from GitHub::

    $ pip install -e git://github.com/bitmazk/django-paypal-express-checkout.git#egg=paypal_express_checkout

Add ``paypal_express_checkout`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...,
        'paypal_express_checkout',
    )

Hook this app into your ``urls.py``::

    urlpatterns = patterns('',
        ...
        url(r'^paypal_express_checkout/$', include('paypal_express_checkout.urls')),
    )


TODO:
Describe settings that need to be set in order for it to work.


Usage
-----

TODO:
Describe usage.

Contribute
----------

If you want to contribute to this project, please perform the following steps::

    # Fork this repository
    # Clone your fork
    $ mkvirtualenv -p python2.7 django-paypal_express_checkout
    $ pip install -r requirements.txt
    $ ./logger/tests/runtests.sh
    # You should get no failing tests

    $ git co -b feature_branch master
    # Implement your feature and tests
    # Describe your change in the CHANGELOG.txt
    $ git add . && git commit
    $ git push origin feature_branch
    # Send us a pull request for your feature branch

Whenever you run the tests a coverage output will be generated in
``tests/coverage/index.html``. When adding new features, please make sure that
you keep the coverage at 100%.


Roadmap
-------

Check the issue tracker on github for milestones and features to come.
