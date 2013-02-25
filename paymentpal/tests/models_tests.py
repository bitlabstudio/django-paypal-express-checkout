"""Tests for the models of the ``paymentpal`` app."""
from django.test import TestCase

from paymentpal.models import PaymentTransaction, PaymentTransactionError


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
