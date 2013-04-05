"""Admins for the models of the ``paypal_express_checkout`` app."""
from django.contrib import admin

from . import models


class ItemAdmin(admin.ModelAdmin):
    """Custom admin for the ``Item`` model."""
    list_display = ['name', 'description_short', 'value']
    search_fields = ['name', 'description']

    def description_short(self, obj):
        return '{0}...'.format(obj.description[:50])


class PaymentTransactionAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransaction`` model."""
    list_display = ['date', 'user', 'transaction_id', 'value', 'status']
    search_fields = [
        'transaction_id', 'status', 'user__email', 'user__usermame']
    list_filter = ['status']


class PaymentTransactionErrorAdmin(admin.ModelAdmin):
    """Custom admin for the ``PaymentTransactionError`` model."""
    list_display = ['date', 'user', 'response_short', 'transaction_id']

    def response_short(self, obj):
        return '{0}...'.format(obj.response[:50])

    def transaction_id(self, obj):
        return obj.transaction_id


class PurchasedItemAdmin(admin.ModelAdmin):
    """Custom admin for the ``PurchasedItem`` model."""
    list_display = [
        'date', 'user', 'transaction', 'item', 'quantity', 'subtotal', 'total',
        'status', ]
    list_filter = [
        'transaction__status', 'item', ]
    search_fields = [
        'transaction__transaction_id', 'user__email', ]

    def date(self, obj):
        return obj.transaction.date

    def subtotal(self, obj):
        return obj.item.value * obj.quantity

    def total(self, obj):
        return obj.transaction.value

    def status(self, obj):
        return obj.transaction.status


admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(
    models.PaymentTransactionError, PaymentTransactionErrorAdmin)
admin.site.register(models.PurchasedItem, PurchasedItemAdmin)
