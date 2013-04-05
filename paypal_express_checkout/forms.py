"""Forms for the ``paypal_express_checkout`` app."""
import httplib
import logging
import urllib
import urllib2
import urlparse

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .constants import PAYMENT_STATUS, PAYPAL_DEFAULTS
from .models import (
    Item,
    PaymentTransaction,
    PaymentTransactionError,
    PurchasedItem,
)
from .settings import API_URL, LOGIN_URL


logger = logging.getLogger(__name__)


class PayPalFormMixin(object):
    """Common methods for the PayPal forms."""
    def call_paypal(self, post_data):
        """
        Gets the PayPal API URL from the settings and posts ``post_data``.

        :param post_data: The full post data for PayPal containing all needed
          information for the current transaction step.

        """
        try:
            response = urllib2.urlopen(
                API_URL, data=urllib.urlencode(post_data))
        except (
                urllib2.HTTPError,
                urllib2.URLError,
                httplib.HTTPException), ex:
            self.log_error(ex)
        else:
            parsed_response = urlparse.parse_qs(response.read())
            return parsed_response

    def log_error(self, error_message, transaction=None):
        """
        Saves error information as a ``PaymentTransactionError`` object.

        :param error_message: The message of the exception or response string
          from PayPal.

        """
        payment_error = PaymentTransactionError()
        payment_error.user = self.user
        payment_error.response = error_message
        payment_error.transaction = transaction
        payment_error.save()
        return payment_error


class DoExpressCheckoutForm(PayPalFormMixin, forms.Form):
    """
    Takes the input from the ``DoExpressCheckoutView``, validates it and
    takes care of the PayPal API operations.

    """
    token = forms.CharField()

    payerID = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        super(DoExpressCheckoutForm, self).__init__(*args, **kwargs)
        try:
            self.transaction = PaymentTransaction.objects.get(
                user=user, transaction_id=self.data['token'])
        except PaymentTransaction.DoesNotExist:
            raise Http404

    def get_post_data(self):
        """Creates the post data dictionary to send to PayPal."""
        post_data = PAYPAL_DEFAULTS
        post_data.update({
            'METHOD': 'DoExpressCheckoutPayment',
            'TOKEN': self.transaction.transaction_id,
            'PAYERID': self.data['payerID'],
            'PAYMENTREQUEST_0_AMT': self.transaction.value,
            'PAYMENTREQUEST_0_NOTIFYURL': settings.HOSTNAME + reverse(
                'ipn_listener'),
        })
        return post_data

    def do_checkout(self):
        """Calls PayPal to make the 'DoExpressCheckoutPayment' procedure."""
        post_data = self.get_post_data()
        parsed_response = self.call_paypal(post_data)
        if parsed_response.get('ACK')[0] == 'Success':
            transaction_id = parsed_response.get(
                'PAYMENTINFO_0_TRANSACTIONID')[0]
            self.transaction.transaction_id = transaction_id
            self.transaction.status = PAYMENT_STATUS['pending']
            self.transaction.save()
            return redirect(reverse('paypal_success'))
        elif parsed_response.get('ACK')[0] == 'Failure':
            self.transaction.status = PAYMENT_STATUS['error']
            self.transaction.save()
            self.log_error(parsed_response, self.transaction)
            return redirect(reverse('paypal_error'))


class SetExpressCheckoutFormMixin(PayPalFormMixin, forms.Form):
    """
    Base form class for all forms invoking the ``SetExpressCheckout`` PayPal
    API operation, providing the general method skeleton.

    Also this is to be used to construct custom forms.

    """
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetExpressCheckoutFormMixin, self).__init__(*args, **kwargs)

    def get_content_object(self):
        """
        Can be overridden to return a different content object for the
        PaymentTransaction model.

        This is useful if you want e.g. have one of your models assigned to the
        transaction for easier identification.

        """
        # TODO for now it should return the user, although I know, that the
        # user is already present in the user field of the PaymentTransaction
        # model.
        # Maybe we can remove the user field safely in exchange for the generic
        # relation only.
        return self.user

    def get_item(self):
        """Obsolete. Just implement ``get_items_and_quantities``."""
        raise NotImplemented

    def get_quantity(self):
        """Obsolete. Just implement ``get_items_and_quantities``."""
        raise NotImplemented

    def get_items_and_quantities(self):
        """
        Returns the items and quantities.

        Should return a list of tuples: ``[(item, quantity), ]``

        """
        logger.warning(
            'Deprecation warning: Please implement get_items_and_quantities on'
            ' your SetExpressCheckoutForm. Do not use get_item and'
            ' get_quantity any more.')
        return [(self.get_item(), self.get_quantity()), ]

    def get_post_data(self, item_quantity_list):
        """Creates the post data dictionary to send to PayPal."""
        post_data = PAYPAL_DEFAULTS
        total_value = 0
        for item, quantity in item_quantity_list:
            if not quantity:
                # If a user chose quantity 0, we don't include it
                continue
            total_value += item.value * quantity
            post_data.update({
                'L_PAYMENTREQUEST_0_NAME0': item.name,
                'L_PAYMENTREQUEST_0_DESC0': item.description,
                'L_PAYMENTREQUEST_0_AMT0': item.value,
                'L_PAYMENTREQUEST_0_QTY0': quantity,
            })

        post_data.update({
            'METHOD': 'SetExpressCheckout',
            'PAYMENTREQUEST_0_AMT': total_value,
            'PAYMENTREQUEST_0_ITEMAMT': total_value,
            'RETURNURL': settings.HOSTNAME + reverse(
                'paypal_confirm', kwargs=self.get_url_kwargs()),
            'CANCELURL': settings.HOSTNAME + reverse(
                'paypal_canceled', kwargs=self.get_url_kwargs()),
        })
        return post_data

    def get_url_kwargs(self):
        """Provide additional url kwargs, by overriding this method."""
        return {}

    def set_checkout(self):
        """
        Calls PayPal to make the 'SetExpressCheckout' procedure.

        :param items: A list of ``Item`` objects.

        """
        item_quantity_list = self.get_items_and_quantities()
        post_data = self.get_post_data(item_quantity_list)

        # making the post to paypal and handling the results
        parsed_response = self.call_paypal(post_data)
        if parsed_response.get('ACK')[0] == 'Success':
            token = parsed_response.get('TOKEN')[0]
            transaction = PaymentTransaction(
                user=self.user,
                date=now(),
                transaction_id=token,
                value=post_data['PAYMENTREQUEST_0_AMT'],
                status=PAYMENT_STATUS['checkout'],
                content_object=self.get_content_object(),
            )
            transaction.save()
            for item, quantity in item_quantity_list:
                if not quantity:
                    continue
                PurchasedItem.objects.create(
                    user=self.user, transaction=transaction, item=item,
                    quantity=quantity)
            return redirect(LOGIN_URL + token)
        elif parsed_response.get('ACK')[0] == 'Failure':
            self.log_error(parsed_response)
            return redirect(reverse('paypal_error'))


class SetExpressCheckoutItemForm(SetExpressCheckoutFormMixin):
    """
    Takes the input from the ``SetExpressCheckoutView``, validates it and
    takes care of the PayPal API operations.

    """
    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        empty_label=None,
        label=_('Item'),
    )

    quantity = forms.IntegerField(
        label=_('Quantity'),
    )

    def get_item(self):
        """Keeping this for backwards compatibility."""
        return self.cleaned_data.get('item')

    def get_quantity(self):
        """Keeping this for backwards compatibility."""
        return self.cleaned_data.get('quantity')

    def get_items_and_quantities(self):
        """
        Returns the items and quantities.

        Should return a list of tuples.

        """
        return [
            (self.get_item(), self.get_quantity()),
        ]
