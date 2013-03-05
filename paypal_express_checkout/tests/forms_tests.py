"""Tests for the forms of the ``paypal_express_checkout`` app."""
from mock import Mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_libs.tests.factories import UserFactory

from paypal_express_checkout.forms import (
    PayPalFormMixin,
    SetExpressCheckoutItemForm,
)
from paypal_express_checkout.tests.factories import ItemFactory


class SetExpressCheckoutItemFormTestCase(TestCase):
    """Tests for the ``SetExpressCheckoutItemForm`` form class."""
    longMessage = True

    def setUp(self):
        self.user = UserFactory()
        self.item = ItemFactory()

        self.paypal_response = {
            'ACK': ['Success'],
            'TOKEN': ['abc123'],
        }

        self.expected_response = {
            'USER': settings.PAYPAL_USER,
            'PWD': settings.PAYPAL_PWD,
            'SIGNATURE': settings.PAYPAL_SIGNATURE,
            'VERSION': '91.0',
            'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
            'METHOD': 'SetExpressCheckout',

            'L_PAYMENTREQUEST_0_NAME0': self.item.name,
            'L_PAYMENTREQUEST_0_DESC0': self.item.description,
            'L_PAYMENTREQUEST_0_AMT0': self.item.value,
            'L_PAYMENTREQUEST_0_QTY0': 1,

            'PAYMENTREQUEST_0_AMT': self.item.value,
            'PAYMENTREQUEST_0_ITEMAMT': self.item.value,
            'RETURNURL': settings.HOSTNAME + reverse(
                'paypal_confirm'),
            'CANCELURL': settings.HOSTNAME + reverse(
                'paypal_canceled')
        }
        self.data = {
            'item': self.item.pk,
            'quantity': 1,
        }

        self.old_call_paypal = PayPalFormMixin.call_paypal
        PayPalFormMixin.call_paypal = Mock(return_value=self.paypal_response)

    def tearDown(self):
        PayPalFormMixin.call_paypal = self.old_call_paypal

    def test_is_valid_and_calls_paypal(self):
        """
        Test if the ``SetExpressCheckoutItemForm`` validates and calls PayPal.

        """
        form = SetExpressCheckoutItemForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid(), msg='The form should be valid.')

        resp = form.set_checkout()
        self.assertEqual(resp.status_code, 302, msg=(
            'Response should redirect.'))
        self.assertEqual(
            resp.items()[1][1], settings.PAYPAL_LOGIN_URL + 'abc123', msg=(
                'Should redirect to PayPal Login.'))

        self.paypal_response.update({
            'ACK': ['Failure']})
        resp = form.set_checkout()
        self.assertEqual(resp.status_code, 302, msg=(
            'Response should redirect.'))
        self.assertEqual(
            resp.items()[1][1], reverse('paypal_error'),
            msg='Should redirect to PaymentErrorView.')
