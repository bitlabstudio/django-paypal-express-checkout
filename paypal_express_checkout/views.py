"""Views for the ``paypal_express_checkout`` app."""
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, TemplateView
from django.utils.decorators import method_decorator

from paypal_express_checkout.forms import (
    DoExpressCheckoutForm,
    SetExpressCheckoutForm,
)


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
