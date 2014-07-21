"""Views for the ``paypal_express_checkout`` app."""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, View
from django.utils.decorators import method_decorator

from django_libs.utils import conditional_decorator

from . import settings
from .constants import PAYMENT_STATUS
from .forms import (
    DoExpressCheckoutForm,
)
from .models import PaymentTransaction
from .signals import payment_completed, payment_status_updated
from .settings import SET_CHECKOUT_FORM


# importing the name of the current form for SetExpressCheckout
class_name = SET_CHECKOUT_FORM.split('.')[-1]
module_name = '.'.join(SET_CHECKOUT_FORM.split('.')[:-1])
module = __import__(module_name, fromlist=[class_name])
SetExpressCheckoutForm = getattr(module, class_name)


class PaymentViewMixin(object):
    """A Mixin to combine common methods of several payment related views."""
    @conditional_decorator(
        method_decorator(login_required),
        not settings.ALLOW_ANONYMOUS_CHECKOUT)
    def dispatch(self, request, *args, **kwargs):
        """Makes sure that the user is logged in."""
        if not settings.ALLOW_ANONYMOUS_CHECKOUT:
            self.user = request.user
        return super(PaymentViewMixin, self).dispatch(request, *args, **kwargs)


class DoExpressCheckoutView(PaymentViewMixin, FormView):
    """
    This view lets the user review and confirm the payment.

    It leads to the ``DoExpressCheckout`` PayPal API operation.

    :attr skip_confirmation: If you set this to ``True``, the user will not
      need to click yet another confirm button, instead, the paypal website
      will load a little bit longer and we will get straight to the success
      view.

    """
    form_class = DoExpressCheckoutForm
    template_name = 'paypal_express_checkout/confirm_checkout.html'
    skip_confirmation = False

    @conditional_decorator(
        method_decorator(login_required),
        not settings.ALLOW_ANONYMOUS_CHECKOUT)
    def dispatch(self, request, *args, **kwargs):
        """Recalls the transaction using the paypal token."""
        # when this view posts to itself it sends the info in the post data
        self.token = request.GET.get('token') or request.POST.get('token')
        self.payerID = request.GET.get('PayerID') or request.POST.get(
            'PayerID')
        try:
            self.transaction = PaymentTransaction.objects.get(
                user=request.user, transaction_id=self.token)
        except PaymentTransaction.DoesNotExist:
            raise Http404

        if self.skip_confirmation:
            self.user = request.user
            self.request = request
            return self.post(request, *args, **kwargs)
        return super(DoExpressCheckoutView, self).dispatch(
            request, *args, **kwargs)

    def form_valid(self, form):
        """When the form is valid, the form should handle the PayPal call."""
        return form.do_checkout()

    def get_context_data(self, **kwargs):
        ctx = super(DoExpressCheckoutView, self).get_context_data(**kwargs)
        ctx.update({
            'value': self.transaction.value,
            'token': self.token,
            'payerid': self.payerID,
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(DoExpressCheckoutView, self).get_form_kwargs()
        kwargs.update({'user': self.user})
        # PayPal makes a GET request with the data, so we check if the GET data
        # is populated and overwrite form data with it.
        if any(self.request.GET):
            kwargs.update({'data': self.request.GET})
        return kwargs


class PaymentCancelView(PaymentViewMixin, TemplateView):
    """The user is redirected to this view, if he cancels the payment."""
    template_name = 'paypal_express_checkout/payment_canceled.html'


class PaymentErrorView(PaymentViewMixin, TemplateView):
    """The user is redirected here once an error occurs during payment."""
    template_name = 'paypal_express_checkout/error.html'


class PaymentSuccessView(PaymentViewMixin, TemplateView):
    """The user is redirected here after a successful PayPal payment."""
    template_name = 'paypal_express_checkout/success.html'


class SetExpressCheckoutView(PaymentViewMixin, FormView):
    """
    This view lets the user initiate the payment.

    It leads to the ``SetExpressCheckout`` PayPal API operation.

    """
    form_class = SetExpressCheckoutForm
    template_name = 'paypal_express_checkout/set_checkout.html'
    redirect = True

    def form_valid(self, form):
        """When the form is valid, the form should handle the PayPal call."""
        return form.set_checkout()

    def get_form_kwargs(self):
        kwargs = super(SetExpressCheckoutView, self).get_form_kwargs()
        kwargs.update({'user': self.user})
        return kwargs


class IPNListenerView(View):
    """This view handles an IPN from PayPal."""
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        payment_status = request.POST.get('payment_status')

        # In case of a refund, we will not create a new transaction. We will
        # alter the status of the original transaction instead.
        if payment_status == PAYMENT_STATUS['refunded']:
            transaction_id = request.POST.get('parent_txn_id')
        else:
            transaction_id = request.POST.get('txn_id')

        try:
            self.payment_transaction = PaymentTransaction.objects.get(
                transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            raise Http404

        return super(IPNListenerView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        payment_status = request.POST.get('payment_status')
        self.payment_transaction.status = payment_status
        self.payment_transaction.save()
        if payment_status == PAYMENT_STATUS['completed']:
            payment_completed.send(self, transaction=self.payment_transaction)
        payment_status_updated.send(self, transaction=self.payment_transaction)
        return HttpResponse()
