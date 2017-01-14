"""Forms for the ``paypal_express_checkout`` app."""
import httplib
import logging
import urllib2
import urlparse

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
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
from .utils import urlencode


logger = logging.getLogger(__name__)


CURRENCYCODE = getattr(settings, 'PAYPAL_CURRENCYCODE', 'USD')


class PayPalFormMixin(object):
    """Common methods for the PayPal forms."""
    def call_paypal(self, api_url, post_data, transaction=None):
        """
        Gets the PayPal API URL from the settings and posts ``post_data``.

        :param api_url: The API endpoint that should be called.
        :param post_data: The full post data for PayPal containing all needed
          information for the current transaction step.
        :param transaction: If you already have a transaction, pass it into
          this method so that it can be logged in case of an error.

        """
        data = urlencode(post_data)
        try:
            response = urllib2.urlopen(api_url, data=data)
        except (
                urllib2.HTTPError,
                urllib2.URLError,
                httplib.HTTPException) as ex:
            self.log_error(
                ex, api_url=api_url, request_data=data,
                transaction=transaction)
        else:
            parsed_response = urlparse.parse_qs(response.read())
            return parsed_response

    def get_cancel_url(self):
        """Returns the paypal cancel url."""
        return settings.HOSTNAME + reverse(
            'paypal_canceled', kwargs=self.get_url_kwargs())

    def get_error_url(self):
        """Returns the url of the payment error page."""
        return reverse('paypal_error')

    def get_notify_url(self):
        """Returns the notification (ipn) url."""
        return settings.HOSTNAME + reverse('ipn_listener')

    def get_return_url(self):
        """Returns the paypal return url."""
        return settings.HOSTNAME + reverse(
            'paypal_confirm', kwargs=self.get_url_kwargs())

    def get_success_url(self):
        """Returns the url of the payment success page."""
        return reverse('paypal_success')

    def log_error(self, error_message, api_url=None, request_data=None,
                  transaction=None):
        """
        Saves error information as a ``PaymentTransactionError`` object.

        :param error_message: The message of the exception or response string
          from PayPal.

        """
        payment_error = PaymentTransactionError()
        payment_error.user = self.user
        payment_error.response = error_message
        payment_error.paypal_api_url = api_url
        payment_error.request_data = request_data
        payment_error.transaction = transaction
        payment_error.save()
        return payment_error


class DoExpressCheckoutForm(PayPalFormMixin, forms.Form):
    """
    Takes the input from the ``DoExpressCheckoutView``, validates it and
    takes care of the PayPal API operations.

    """
    token = forms.CharField()

    PayerID = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(DoExpressCheckoutForm, self).__init__(*args, **kwargs)
        try:
            self.transaction = PaymentTransaction.objects.get(
                user=user, transaction_id=self.data['token'])
        except PaymentTransaction.DoesNotExist:
            raise Http404

    def get_post_data(self):
        """Creates the post data dictionary to send to PayPal."""
        post_data = PAYPAL_DEFAULTS.copy()
        items = self.transaction.purchaseditem_set.all()
        currency = None
        if len(items) != 0:
            if getattr(items[0].item, 'currency', None) is not None:
                currency = items[0].item.currency
            elif getattr(
                    items[0].content_object, 'currency', None) is not None:
                currency = items[0].content_object.currency
        if not currency:
            currency = CURRENCYCODE
        post_data.update({
            'METHOD': 'DoExpressCheckoutPayment',
            'TOKEN': self.transaction.transaction_id,
            'PAYERID': self.data['PayerID'],
            'PAYMENTREQUEST_0_AMT': self.transaction.value,
            'PAYMENTREQUEST_0_NOTIFYURL': self.get_notify_url(),
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
        })
        return post_data

    def do_checkout(self):
        """Calls PayPal to make the 'DoExpressCheckoutPayment' procedure."""
        post_data = self.get_post_data()
        api_url = API_URL
        parsed_response = self.call_paypal(api_url, post_data)
        if parsed_response.get('ACK')[0] == 'Success':
            transaction_id = parsed_response.get(
                'PAYMENTINFO_0_TRANSACTIONID')[0]
            self.transaction.transaction_id = transaction_id
            self.transaction.status = PAYMENT_STATUS['pending']
            self.transaction.save()
            return redirect(self.get_success_url())
        elif parsed_response.get('ACK')[0] == 'Failure':
            self.transaction.status = PAYMENT_STATUS['canceled']
            self.transaction.save()
            # we have to do urlencode here to make the post data more readable
            # in the error log
            post_data_encoded = urlencode(post_data)
            self.log_error(
                parsed_response, api_url, request_data=post_data_encoded,
                transaction=self.transaction)
            return redirect(self.get_error_url())


class SetExpressCheckoutFormMixin(PayPalFormMixin, forms.Form):
    """
    Base form class for all forms invoking the ``SetExpressCheckout`` PayPal
    API operation, providing the general method skeleton.

    Also this is to be used to construct custom forms.

    :param user: The user making the purchase
    :param redirect: If ``True``, the form will return a HttpResponseRedirect,
      otherwise it will only return the redirect URL. This can be useful if
      you want to use this form in an AJAX view.

    """
    def __init__(self, user, redirect=True, *args, **kwargs):
        self.redirect = redirect
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
        raise NotImplementedError

    def get_quantity(self):
        """Obsolete. Just implement ``get_items_and_quantities``."""
        raise NotImplementedError

    def get_items_and_quantities(self):
        """
        Returns the items and quantities and content objects.

        Content objects are optional, return None if you don't need it.

        Should return a list of tuples:
        ``[(item, quantity, content_object), ]``

        """
        logger.warning(
            'Deprecation warning: Please implement get_items_and_quantities on'
            ' your SetExpressCheckoutForm. Do not use get_item and'
            ' get_quantity any more.')
        return [(self.get_item(), self.get_quantity(), None), ]

    def get_post_data(self, item_quantity_list):
        """Creates the post data dictionary to send to PayPal."""
        post_data = PAYPAL_DEFAULTS.copy()
        total_value = 0
        item_index = 0
        for item, quantity, content_type in item_quantity_list:
            if not quantity:
                # If a user chose quantity 0, we don't include it
                continue
            total_value += item.value * quantity
            post_data.update({
                'L_PAYMENTREQUEST_0_NAME{0}'.format(
                    item_index): item.name,
                'L_PAYMENTREQUEST_0_DESC{0}'.format(
                    item_index): item.description,
                'L_PAYMENTREQUEST_0_AMT{0}'.format(
                    item_index): item.value,
                'L_PAYMENTREQUEST_0_QTY{0}'.format(
                    item_index): quantity,
            })
            item_index += 1

        if (
                len(item_quantity_list) != 0 and
                getattr(item_quantity_list[0][0], 'currency') is not None):
            currency = item_quantity_list[0][0].currency
        else:
            currency = CURRENCYCODE

        post_data.update({
            'METHOD': 'SetExpressCheckout',
            'PAYMENTREQUEST_0_AMT': total_value,
            'PAYMENTREQUEST_0_ITEMAMT': total_value,
            'RETURNURL': self.get_return_url(),
            'CANCELURL': self.get_cancel_url(),
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
        })
        return post_data

    def get_url_kwargs(self):
        """Provide additional url kwargs, by overriding this method."""
        return {}

    def post_transaction_save(self, transaction, item_quantity_list):
        """
        Override this method if you need to create further objects.

        Once we got a successful response from PayPal we can create a
        Transaction with status "checkout". You might want to create or
        manipulate further objects in your app at this point.

        For example you might ask for user's the t-shirt size on your checkout
        form. This a good place to save the user's choice on the UserProfile.

        """
        return

    def set_checkout(self):
        """
        Calls PayPal to make the 'SetExpressCheckout' procedure.

        :param items: A list of ``Item`` objects.

        """
        item_quantity_list = self.get_items_and_quantities()
        post_data = self.get_post_data(item_quantity_list)
        api_url = API_URL

        # making the post to paypal and handling the results
        parsed_response = self.call_paypal(api_url, post_data)
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
            self.post_transaction_save(transaction, item_quantity_list)
            for item, quantity, content_object in item_quantity_list:
                if not quantity:
                    continue
                purchased_item_kwargs = {
                    'user': self.user,
                    'transaction': transaction,
                    'quantity': quantity,
                    'price': item.value,
                    'identifier': item.identifier,
                }

                if content_object:
                    purchased_item_kwargs.update({
                        'object_id': content_object.pk,
                        'content_type': ContentType.objects.get_for_model(
                            content_object),
                    })

                if item.pk:
                    purchased_item_kwargs.update({'item': item, })

                PurchasedItem.objects.create(**purchased_item_kwargs)
            if self.redirect:
                return redirect(LOGIN_URL + token)
            return LOGIN_URL + token
        elif parsed_response.get('ACK')[0] == 'Failure':
            post_data_encoded = urlencode(post_data)
            self.log_error(
                parsed_response, api_url=api_url,
                request_data=post_data_encoded)
            return redirect(self.get_error_url())


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
            (self.get_item(), self.get_quantity(), None),
        ]
