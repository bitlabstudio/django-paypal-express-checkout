"""Constants for the ``paymentpal`` app."""

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
