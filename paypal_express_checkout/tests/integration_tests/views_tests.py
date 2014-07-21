"""Tests for the views of the ``paypal_express_checkout`` app."""
from mock import Mock, patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from ..factories import (
    ItemFactory,
    PaymentTransactionFactory,
)
from ...forms import PayPalFormMixin
from ...models import PaymentTransaction
from ...signals import payment_completed
from ...views import DoExpressCheckoutView


class PaymentViewTestCaseMixin(ViewTestMixin):
    def should_redirect_to_login_when_anonymous(self):
        """Custom method to overwrite the one from django_libs."""
        url = self.get_url()
        resp = self.client.get(url)
        self.assertRedirects(resp, '{0}?next={1}'.format('/', url))


class DoExpressCheckoutViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``DoExpressCheckoutView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_confirm'

    def get_post_data(self):
        return {
            'token': self.transaction.transaction_id,
            'payerID': 'testpayerID',
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

    def get_req_and_view(self):
        self.login(self.user)
        req = RequestFactory().get('/', data=self.get_post_data())
        req.user = self.user
        view = DoExpressCheckoutView()
        return req, view

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.user, data=self.get_post_data())
        self.is_callable('post', data=self.get_post_data())
        self.is_not_callable()

    def test_skip_confirmation(self):
        req, view = self.get_req_and_view()
        view.skip_confirmation = True
        view.post = Mock()
        view.dispatch(req)
        self.assertEqual(view.post.call_count, 1, msg=(
            'When called with skip_confirmation=True, the view will not'
            ' render the template but execute the post handler instead'
            ' of the get handler'))

    def test_form_valid(self):
        req, view = self.get_req_and_view()
        form_mock = Mock()
        view.form = form_mock
        view.dispatch(req)
        view.form_valid(view.form)
        self.assertEqual(form_mock.do_checkout.call_count, 1, msg=(
            'When the form is valid, the view should execute and return the'
            ' do_checkout method of the form'))


class PaymentCancelViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentCancelView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_canceled'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class PaymentErrorViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentErrorView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_error'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class PaymentSuccessViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``PaymentSuccessView`` view class."""
    longMessage = True

    def get_view_name(self):
        return 'paypal_success'

    def setUp(self):
        self.user = UserFactory()

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.should_be_callable_when_authenticated(self.user)


class SetExpressCheckoutViewTestCase(PaymentViewTestCaseMixin, TestCase):
    """Tests for the ``SetExpressCheckoutView`` view class."""
    longMessage = True

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
        self.is_callable('post', data=self.data, user=self.user)


class IPNListenerViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``IPNListenerView`` view class."""
    longMessage = True

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
        self.is_callable(method='post', data=self.valid_data)
        self.assertEqual(self.received_transaction, self.transaction, msg=(
            'When the IPNListenerView is called, it should send a signal.'))
        self.is_not_callable()

    def test_refund_transaction(self):
        self.valid_data = {
            'txn_id': 'SOME_NEW_ID',
            'parent_txn_id': self.transaction.transaction_id,
            'payment_status': 'Refunded'
        }
        self.is_callable(method='post', data=self.valid_data)
        transaction = PaymentTransaction.objects.get(pk=self.transaction.pk)
        self.assertEqual(transaction.status, 'Refunded', msg=(
            'When the IPNListenerView is called, it should set the'
            ' to the Refunded status.'))
