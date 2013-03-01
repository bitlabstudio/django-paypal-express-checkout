"""Constants for the ``paypal_express_checkout`` app."""
from django.conf import settings


# Common values for a payment status.

PAYMENT_STATUS = {
    'checkout': 'checkout',
    'pending': 'pending',
    'canceled': 'canceled',
    'completed': 'completed',
}

STATUS_CHOICES = (
    (PAYMENT_STATUS['checkout'], 'checkout'),
    (PAYMENT_STATUS['pending'], 'pending'),
    (PAYMENT_STATUS['canceled'], 'canceled'),
    (PAYMENT_STATUS['completed'], 'completed'),
)


PAYPAL_DEFAULTS = {
    'USER': settings.API_USER,
    'PWD': settings.API_PASSWORD,
    'SIGNATURE': settings.API_SIGNATURE,
    'VERSION': '91.0',
    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
}

if settings.SALE_DESCRIPTION:
    PAYPAL_DEFAULTS.update({
        'PAYMENTREQUEST_0_DESC': settings.SALE_DESCRIPTION})
