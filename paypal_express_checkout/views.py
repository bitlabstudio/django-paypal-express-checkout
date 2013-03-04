"""Views for the ``paypal_express_checkout`` app."""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, View
from django.utils.decorators import method_decorator

from .forms import (
    DoExpressCheckoutForm,
    SetExpressCheckoutForm,
)
from .models import PaymentTransaction
from .signals import payment_completed


class PaymentViewMixin(object):
    """A Mixin to combine common methods of several payment related views."""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Makes sure that the user is logged in."""
        self.user = request.user
        return super(PaymentViewMixin, self).dispatch(request, *args, **kwargs)


class DoExpressCheckoutView(PaymentViewMixin, FormView):
    """
    This view lets the user review and confirm the payment.

    It leads to the ``DoExpressCheckout`` PayPal API operation.

    """
    form_class = DoExpressCheckoutForm
    template_name = 'paypal_express_checkout/confirm_checkout.html'

    def form_valid(self, form):
        """When the form is valid, the form should handle the PayPal call."""
        return form.do_checkout()

    def get_form_kwargs(self):
        kwargs = super(DoExpressCheckoutView, self).get_form_kwargs()
        kwargs.update({'user': self.user})
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
        transaction_id = request.POST.get('txn_id')
        try:
            self.payment_transaction = PaymentTransaction.objects.get(
                transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            raise Http404
        return super(IPNListenerView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        payment_status = request.POST.get('payment_status')
        if payment_status == 'Completed':
            payment_completed.send(self, transaction=self.payment_transaction)
            self.payment_transaction.status = 'completed'
            self.payment_transaction.save()
            return HttpResponse()
        elif payment_status == 'Expired' or payment_status == 'Denied'\
                or payment_status == 'Failed':
            self.payment_transaction.status = 'canceled'
            self.payment_transaction.save()
            return HttpResponse()
