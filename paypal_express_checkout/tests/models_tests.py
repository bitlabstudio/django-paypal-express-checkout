"""Tests for the models of the ``paypal_express_checkout`` app."""
from django.test import TestCase

from paypal_express_checkout.models import (
    PaymentTransaction,
    PaymentTransactionError,
)


class PaymentTransactionTestCase(TestCase):
    """Tests for the ``PaymentTransaction`` model."""
    longMessage = True

    def test_instantiation(self):
        """Testing instantiation of the ``PaymentTransaction`` model."""
        transaction = PaymentTransaction()
        self.assertTrue(transaction)


class PaymentTransactionErrorTestCase(TestCase):
    """Tests for the ``PaymentTransactionError`` model."""
    longMessage = True

    def test_instantiation(self):
        """Testing instantiation of the ``PaymentTransactionError`` model."""
        error = PaymentTransactionError()
        self.assertTrue(error)
