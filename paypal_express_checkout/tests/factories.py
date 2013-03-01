"""Factories for the ``paypal_express_checkout`` app."""
import factory
from decimal import Decimal

from django_libs.tests.factories import UserFactory

from paypal_express_checkout.models import Item, PaymentTransaction


class ItemFactory(factory.Factory):
    FACTORY_FOR = Item

    name = factory.Sequence(lambda x: 'item{0}'.format(x))
    description = factory.Sequence(lambda x: 'item descriptio{0}'.format(x))
    value = Decimal('10.00')


class PaymentTransactionFactory(factory.Factory):
    FACTORY_FOR = PaymentTransaction

    user = factory.SubFactory(UserFactory)
    transaction_id = factory.Sequence(lambda x: '123abc{0}'.format(x))
    value = Decimal('10.00')
