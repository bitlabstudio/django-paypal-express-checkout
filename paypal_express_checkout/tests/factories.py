"""Factories for the ``paypal_express_checkout`` app."""
import factory
from decimal import Decimal

from django_libs.tests.factories import UserFactory

from .. import models


class ItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Item

    name = factory.Sequence(lambda x: 'item{0}'.format(x))
    description = factory.Sequence(lambda x: 'item descriptio{0}'.format(x))
    value = Decimal('10.00')


class PaymentTransactionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.PaymentTransaction

    user = factory.SubFactory(UserFactory)
    transaction_id = factory.Sequence(lambda x: '123abc{0}'.format(x))
    value = Decimal('10.00')


class PurchasedItemFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.PurchasedItem

    user = factory.SubFactory(UserFactory)
    transaction = factory.LazyAttribute(
        lambda x: PaymentTransactionFactory(user=x.user))
    item = factory.SubFactory(ItemFactory)
    quantity = 1
