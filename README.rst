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
        url(r'^checkout/', include('paypal_express_checkout.urls')),
    )


Add your hostname to the following settting: ::

    HOSTNAME = 'http://example.com'  # without trailing slash

In case you want to test your checkout view in the browser locally, you need
to install something like `localtunnel <http://localtunnel.me/>`_ and set
your hostname to your localtunnel url: ::

    HOSTNAME = 'http://XXXX.localtunnel.me'

For testing and development you might want to set the PayPal URLs to the
sandbox ones in your ``local_settings.py``: ::

    PAYPAL_API_URL = 'https://api-3t.sandbox.paypal.com/nvp'
    PAYPAL_LOGIN_URL = (
        'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token='
    )

The following setting will be the description of all payments that are
displayed when the user logs into his PayPal account for checkout: ::

    SALE_DESCRIPTION = 'Your payment to Foobar Inc.'

.. hint::

    This is not the description of an Item!

Finally you need to set the following settings to the user, password and
signature PayPal will provide you with: ::

    PAYPAL_USER = 'username_merchant_api1.gmail.com'
    PAYPAL_PWD = 'your api password'
    PAYPAL_SIGNATURE = 'your api signature'

Don't forget to run the South migrations::

    ./manage.py migrate paypal_express_checkout


Settings
--------

If you want to allow anonymous checkout set the
``PAYPAL_ALLOW_ANONYMOUS_CHECKOUT`` to ``True``:::

    PAYPAL_ALLOW_ANONYMOUS_CHECKOUT = True  # Defaults to False


Usage
-----

**Creating Items**

First you should add an ``Item`` to your project. They can be easily added and
updated via the Django admin.
There you set ``Item.name`` as the display name of your item,
``Item.description`` for a further description and ``Item.value`` for the price
of this item.
Your customer will then be able to chose between the items you provide and set
a quantity for how much he wants to buy.

**Overriding the form**

If you seek for a more complex solution, at this point we provide the
``SetExpressCheckoutFormMixin`` to allow you to customize the form that is used
to process the checkout procedure.
The minimum implementation should include: ::

    class MyForm(SetExpressCheckoutFormMixin):
        def get_items_and_quantities(self):
            item = Item.objects.get(pk=1)
            quantity = 1
            return [(item, quantity), ]

Have a look at our ``paypal_express_checkout.forms.SetExpressCheckoutForm``
example implementation for a better understanding.

Further we supply a simpe settings hook to tell the app, what new form to use.
Just set ``PAYPAL_SET_CHECKOUT_FORM`` to the correct form class like so:::

    PAYPAL_SET_CHECKOUT_FORM = 'myproject.forms.MyForm'


**Logging**

Each payment is logged in our provided ``PaymentTransaction`` model.
It can also easily be accessed via Django admin and will provide you with
information to identify every payment in every status.

Occasionally there might be an error during the payment process, that the will
be logged in the ``PaymentTransactionError`` model.
It stores information about exceptions or errorous PayPal responses that occur
during a payment.

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

Updating from v1.2 and below
----------------------------

v1.3 of this app has updated the ``factory_boy`` requirements to >2.0.0
``factory_boy`` though has a dependency for setuptools>=0.8, which you need to
install before upgrading your virtual environment. Otherwise running ``pip
install --upgrade -r requirements.txt`` will fail.


Roadmap
-------

Check the issue tracker on github for milestones and features to come.
