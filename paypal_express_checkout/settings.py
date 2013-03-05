"""Settings for the ``paypal_express_checkout`` app."""
from django.conf import settings

SET_CHECKOUT_FORM = getattr(
    settings, 'PAYPAL_SET_CHECKOUT_FORM',
    'paypal_express_checkout.forms.SetExpressCheckoutItemForm')
