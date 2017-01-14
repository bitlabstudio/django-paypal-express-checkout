"""Tests for the views of the ``paypal_express_checkout`` app."""
from mock import Mock, patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewRequestFactoryTestMixin

from ..factories import (
    ItemFactory,
    PaymentTransactionFactory,
)
from ...forms import PayPalFormMixin
from ...models import PaymentTransaction
from ...signals import payment_completed
from ... import views


class DoExpressCheckoutViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``DoExpressCheckoutView`` view class."""
    view_class = views.DoExpressCheckoutView

    def get_view_name(self):
        return 'paypal_confirm'

    def get_post_data(self):
        return {
            'token': self.transaction.transaction_id,
            'PayerID': 'testpayerID',
        }

    def setUp(self):
        self.user = UserFactory()
        self.transaction = PaymentTransactionFactory(user=self.user)
        self.item = ItemFactory()

        self.paypal_response = {
            'ACK': ['Success'],
            'TOKEN': ['abc123'],
            'PAYMENTINFO_0_TRANSACTIONID': ['abc123']
        }

        self.data = {
            'item': self.item.pk,
            'quantity': 1,
        }

        self.old_call_paypal = PayPalFormMixin.call_paypal
        PayPalFormMixin.call_paypal = Mock(return_value=self.paypal_response)

    def tearDown(self):
        PayPalFormMixin.call_paypal = self.old_call_paypal

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.user, data=self.get_post_data())
        self.is_postable(user=self.user, data=self.get_post_data(),
                         to_url_name='paypal_success')
        self.is_not_callable(user=self.user)


class PaymentCancelViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``PaymentCancelView`` view class."""
    view_class = views.PaymentCancelView

    def get_view_name(self):
        return 'paypal_canceled'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.user)


class PaymentErrorViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``PaymentErrorView`` view class."""
    view_class = views.PaymentErrorView

    def get_view_name(self):
        return 'paypal_error'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.user)


class PaymentSuccessViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``PaymentSuccessView`` view class."""
    view_class = views.PaymentSuccessView

    def get_view_name(self):
        return 'paypal_success'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.user)


class SetExpressCheckoutViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``SetExpressCheckoutView`` view class."""
    view_class = views.SetExpressCheckoutView

    def get_view_name(self):
        return 'paypal_checkout'

    def get_post_data(self):
        return {
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

    def setUp(self):
        self.user = UserFactory()
        self.item = ItemFactory()

        self.paypal_response = {
            'ACK': ['Success'],
            'TOKEN': ['abc123'],
        }

        self.data = {
            'item': self.item.pk,
            'quantity': 1,
        }

    @patch.object(PayPalFormMixin, 'call_paypal')
    def test_view(self, call_paypal_mock):
        call_paypal_mock.return_value = self.paypal_response
        self.should_redirect_to_login_when_anonymous()
        self.is_postable(
            data=self.data, user=self.user,
            to=('https://www.sandbox.paypal.com/cgi-bin/webscr'
                '?cmd=_express-checkout&token=abc123'))


class IPNListenerViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``IPNListenerView`` view class."""
    view_class = views.IPNListenerView

    def get_view_name(self):
        return 'ipn_listener'

    def receive(self, signal, sender, transaction):
        self.signal = signal
        self.sender = sender
        self.received_transaction = transaction

    def setUp(self):
        self.transaction = PaymentTransactionFactory()
        self.valid_data = {
            'txn_id': self.transaction.transaction_id,
            'payment_status': 'Completed',
        }
        self.ipn_received = False
        self.signal = payment_completed.connect(self.receive)

    def test_is_callable_and_sends_signal(self):
        self.is_postable(data=self.valid_data, ajax=True)
        self.assertEqual(self.received_transaction, self.transaction, msg=(
            'When the IPNListenerView is called, it should send a signal.'))
        self.is_not_callable()

    def test_refund_transaction(self):
        self.valid_data = {
            'txn_id': 'SOME_NEW_ID',
            'parent_txn_id': self.transaction.transaction_id,
            'payment_status': 'Refunded'
        }
        self.is_postable(data=self.valid_data, ajax=True)
        transaction = PaymentTransaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(transaction.status, 'Refunded', msg=(
            'When the IPNListenerView is called, it should set the'
            ' to the Refunded status.'))
