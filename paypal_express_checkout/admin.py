"""Admins for the models of the ``paypal_express_checkout`` app."""
from django.contrib import admin

from .models import Item, PaymentTransaction, PaymentTransactionError


class ItemAdmin(admin.ModelAdmin):
    """Custom admin for the ``Item`` model."""
    list_display = ('name', 'description_short', 'value')
    search_fields = ['name', 'description']

    def description_short(self, obj):
        return '{0}...'.format(obj.description[:50])


class PaymentTransactionAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransaction`` model."""
    list_display = ('date', 'user', 'transaction_id', 'value', 'status')
    search_fields = [
        'transaction_id', 'status', 'user__email', 'user__usermame']
    list_filter = ['status']


class PaymentTransactionErrorAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransactionError`` model."""
    list_display = ('date', 'user', 'response_short', 'transaction_id')

    def response_short(self, obj):
        return '{0}...'.format(obj.response[:50])

    def transaction_id(self, obj):
        return obj.transaction_id

admin.site.register(Item, ItemAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(PaymentTransactionError, PaymentTransactionErrorAdmin)
