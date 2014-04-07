"""The urls for the ``paypal_express_checkout`` app."""
from django.conf.urls import patterns, url

from paypal_express_checkout.views import (
    DoExpressCheckoutView,
    IPNListenerView,
    PaymentCancelView,
    PaymentErrorView,
    PaymentSuccessView,
    SetExpressCheckoutView,
)


urlpatterns = patterns(
    '',
    url(
        r'^$',
        SetExpressCheckoutView.as_view(),
        name='paypal_checkout'
    ),

    url(
        r'^confirm/$',
        DoExpressCheckoutView.as_view(),
        name='paypal_confirm',
    ),

    url(
        r'^canceled/$',
        PaymentCancelView.as_view(),
        name='paypal_canceled',
    ),

    url(
        r'^error/$',
        PaymentErrorView.as_view(),
        name='paypal_error',
    ),

    url(
        r'^success/$',
        PaymentSuccessView.as_view(),
        name='paypal_success',
    ),

    url(
        r'ipn/$',
        IPNListenerView.as_view(),
        name='ipn_listener',
    ),
)
