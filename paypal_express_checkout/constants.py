"""Constants for the ``paypal_express_checkout`` app."""
from django.conf import settings


# Common values for a payment status.

PAYMENT_STATUS = {
    # app status values
    'checkout': 'Checkout',
    'pending': 'Pending',
    'canceled': 'Canceled',

    # paypal status values
    'completed': 'Completed',
    'canceled_Reversal': 'Canceled_Reversal',
    'created': 'Created',
    'denied': 'Denied',
    'expired': 'Expired',
    'failed': 'Failed',
    'refunded': 'Refunded',
    'reversed': 'Reversed',
    'processed': 'Processed',
    'voided': 'Voided',
}

STATUS_CHOICES = (
    (PAYMENT_STATUS['checkout'], 'Checkout'),
    (PAYMENT_STATUS['pending'], 'Pending'),
    (PAYMENT_STATUS['canceled'], 'Canceled'),
    (PAYMENT_STATUS['completed'], 'Completed'),
    (PAYMENT_STATUS['canceled_Reversal'], 'Canceled_Reversal'),
    (PAYMENT_STATUS['created'], 'Created'),
    (PAYMENT_STATUS['denied'], 'Denied'),
    (PAYMENT_STATUS['expired'], 'Expired'),
    (PAYMENT_STATUS['failed'], 'Failed'),
    (PAYMENT_STATUS['refunded'], 'Refunded'),
    (PAYMENT_STATUS['reversed'], 'Reversed'),
    (PAYMENT_STATUS['processed'], 'Processed'),
    (PAYMENT_STATUS['voided'], 'Voided'),
)


PAYPAL_DEFAULTS = {
    'USER': settings.PAYPAL_USER,
    'PWD': settings.PAYPAL_PWD,
    'SIGNATURE': settings.PAYPAL_SIGNATURE,
    'VERSION': '91.0',
    'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
}

if settings.SALE_DESCRIPTION:
    PAYPAL_DEFAULTS.update({
        'PAYMENTREQUEST_0_DESC': settings.SALE_DESCRIPTION})
