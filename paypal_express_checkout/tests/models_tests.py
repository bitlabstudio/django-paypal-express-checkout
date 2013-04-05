"""Tests for the models of the ``paypal_express_checkout`` app."""
from django.test import TestCase

from .. import models
from . import factories


class PaymentTransactionTestCase(TestCase):
    """Tests for the ``PaymentTransaction`` model."""
    longMessage = True

    def test_instantiation(self):
        """Testing instantiation of the ``PaymentTransaction`` model."""
        transaction = models.PaymentTransaction()
        self.assertTrue(transaction)


class PaymentTransactionErrorTestCase(TestCase):
    """Tests for the ``PaymentTransactionError`` model."""
    longMessage = True

    def test_instantiation(self):
        """Testing instantiation of the ``PaymentTransactionError`` model."""
        error = models.PaymentTransactionError()
        self.assertTrue(error)


class PurchasedItemTestCase(TestCase):
    """Tests for the ``PurchasedItem`` model."""
    longMessage = True

    def test_model(self):
        instance = factories.PurchasedItemFactory()
        self.assertTrue(instance.pk)
