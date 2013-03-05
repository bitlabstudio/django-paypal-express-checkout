"""Settings for the ``paypal_express_checkout`` app."""
from django.conf import settings

CHECKOUT_FORM = getattr(
    settings, 'PAYPAL_CHECKOUT_FORM',
    'paypal_express_checkout.forms.SetExpressCheckoutItemForm')
