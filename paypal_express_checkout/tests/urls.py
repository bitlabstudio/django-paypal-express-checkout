"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
zR you know, every app must be hooked into yout main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.http import HttpResponse


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', lambda req: HttpResponse('Dummy home view'), name='dummy_home'),
    url(r'^paypal/', include('paypal_express_checkout.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
