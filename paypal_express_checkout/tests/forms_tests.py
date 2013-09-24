"""Tests for the forms of the ``paypal_express_checkout`` app."""
from mock import Mock, PropertyMock, patch
from httplib import HTTPException

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase

from django_libs.tests.factories import UserFactory

from ..forms import (
    DoExpressCheckoutForm,
    PayPalFormMixin,
    SetExpressCheckoutFormMixin,
    SetExpressCheckoutItemForm,
)
from ..models import PurchasedItem
from ..constants import PAYPAL_DEFAULTS
from ..settings import API_URL
from .factories import ItemFactory, PaymentTransactionFactory
from ..settings import LOGIN_URL


class PayPalFormMixinTestCase(TestCase):
    """Tests for the ``PayPalFormMixin`` class."""
    longMessage = True

    def setUp(self):
        super(PayPalFormMixinTestCase, self).setUp()
        self.paypal_response = 'ACK=Success&TOKEN=abc123'

    @patch('paypal_express_checkout.forms.urllib2')
    def test_call_paypal(self, urllib2_mock):
        mixin = PayPalFormMixin()

        response_mock = Mock()
        response_mock.read = Mock(return_value=self.paypal_response)
        urllib2_mock.urlopen.return_value = response_mock
        response = mixin.call_paypal(API_URL, {})
        self.assertEqual(response['ACK'], ['Success'], msg=(
            'Should parse the response from paypal and return it as a dict'))

        with patch.object(mixin, 'log_error') as log_error_mock:
            urllib2_mock.urlopen = PropertyMock(side_effect=HTTPException)
            mixin.call_paypal(API_URL, {})
            self.assertEqual(log_error_mock.call_count, 1, msg=(
                'Should log an error if calling the PayPal API fails.'))


class DoExpressCheckoutFormTestCase(TestCase):
    """Tests for the ``DoExpressCheckoutForm`` form class."""
    longMessage = True

    def setUp(self):
        self.token = 'abc123'
        self.transaction = PaymentTransactionFactory(transaction_id=self.token)
        self.user = self.transaction.user
        self.valid_response = {'ACK': ['Success'],
                               'PAYMENTINFO_0_TRANSACTIONID': [self.token]}
        self.invalid_response = {'ACK': ['Failure']}
        self.valid_data = {'token': self.token, 'PayerID': 'PAYERID123'}

    @patch.object(PayPalFormMixin, 'call_paypal')
    def test_form(self, call_paypal_mock):
        call_paypal_mock.return_value = self.valid_response
        form = DoExpressCheckoutForm(user=self.user, data=self.valid_data)
        self.assertTrue(form.is_valid, msg='The form should be valid.')

        resp = form.do_checkout()
        self.assertEqual(resp['Location'], reverse('paypal_success'))

        call_paypal_mock.return_value = self.invalid_response
        form = DoExpressCheckoutForm(user=self.user, data=self.valid_data)
        self.assertTrue(form.is_valid, msg='The form should be valid.')

        resp = form.do_checkout()
        self.assertEqual(resp['Location'], reverse('paypal_error'))

        self.transaction.delete()
        self.assertRaises(Http404, DoExpressCheckoutForm,
                          **{'user': self.user, 'data': self.valid_data})


class SetExpressCheckoutFormMixinTestCase(TestCase):
    """Tests for the ``SetExpressCheckoutFormMixin`` mixin."""
    longMessage = True
    maxDiff = None

    def setUp(self):
        self.user = UserFactory()
        self.item1 = ItemFactory(name='item1')
        self.item2 = ItemFactory(name='item2')
        self.item_list = [(self.item1, 1, None), (self.item2, 0, None)]
        self.expected_post_data = {
            'L_PAYMENTREQUEST_0_NAME0': self.item1.name,
            'L_PAYMENTREQUEST_0_DESC0': self.item1.description,
            'L_PAYMENTREQUEST_0_AMT0': self.item1.value,
            'L_PAYMENTREQUEST_0_QTY0': 1,
            'METHOD': 'SetExpressCheckout',
            'PAYMENTREQUEST_0_AMT': self.item1.value,
            'PAYMENTREQUEST_0_ITEMAMT': self.item1.value,
            'RETURNURL': settings.HOSTNAME + reverse('paypal_confirm'),
            'CANCELURL': settings.HOSTNAME + reverse('paypal_canceled'),
            'PAYMENTREQUEST_0_CURRENCYCODE': 'USD',
        }
        self.expected_post_data.update(PAYPAL_DEFAULTS.copy())
        self.token = 'abc123'
        self.valid_response = {'ACK': ['Success'], 'TOKEN': [self.token]}
        self.invalid_response = {'ACK': ['Failure']}

    @patch.object(PayPalFormMixin, 'call_paypal')
    def test_mixin(self, call_paypal_mock):
        form = SetExpressCheckoutFormMixin(self.user)
        self.assertRaises(NotImplementedError, form.get_item)
        self.assertRaises(NotImplementedError, form.get_quantity)
        self.assertRaises(NotImplementedError, form.get_items_and_quantities)
        self.assertEqual(form.get_post_data(self.item_list),
                         self.expected_post_data)

        old_item_and_qty = SetExpressCheckoutFormMixin.get_items_and_quantities
        SetExpressCheckoutFormMixin.get_items_and_quantities = Mock(
            return_value=self.item_list)
        form = SetExpressCheckoutFormMixin(self.user)

        call_paypal_mock.return_value = self.valid_response
        resp = form.set_checkout()
        self.assertEqual(resp['Location'], LOGIN_URL + self.token)

        call_paypal_mock.return_value = self.invalid_response
        resp = form.set_checkout()
        self.assertEqual(resp['Location'], reverse('paypal_error'))

        SetExpressCheckoutFormMixin.get_items_and_quantities = old_item_and_qty


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
        self.assertEqual(PurchasedItem.objects.all().count(), 1, msg=(
            'Should create a PurchasedItem object when saving the'
            ' transaction'))

        self.paypal_response.update({
            'ACK': ['Failure']})
        resp = form.set_checkout()
        self.assertEqual(resp.status_code, 302, msg=(
            'Response should redirect.'))
        self.assertEqual(
            resp.items()[1][1], reverse('paypal_error'),
            msg='Should redirect to PaymentErrorView.')
