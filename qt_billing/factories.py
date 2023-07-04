import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from qt_utils.model_loaders import (
    get_product_util_model,
    get_stripe_product_model,
    get_unique_selling_point_model,
    get_unique_selling_point_model_through_model,
)


class UniqueSellingPointFactory(DjangoModelFactory):
    class Meta:
        model = get_unique_selling_point_model()

    description_en = factory.Faker("sentence", nb_words=6, locale="en_US")
    description_nl = factory.Faker("sentence", nb_words=6, locale="nl_NL")


class ProductFactory(DjangoModelFactory):
    """
    Create a Product (Stripe) model
    """

    class Meta:
        model = get_stripe_product_model()

    id = factory.LazyAttribute(lambda obj: f"prod_{FuzzyText(length=15).fuzz()}")
    name = factory.Faker("word")
    livemode = False


class ProductUtilFactory(DjangoModelFactory):
    """
    Creates a ProductUtil model
    """

    class Meta:
        model = get_product_util_model()

    product = factory.SubFactory(ProductFactory)
    unique_selling_points = factory.RelatedFactoryList(
        "qt_billing.factories.ProductUniqueSellingPointThroughModelFactory",
        factory_related_name="product_util",
        size=3,
    )


class ProductUniqueSellingPointThroughModelFactory(DjangoModelFactory):
    class Meta:
        model = get_unique_selling_point_model_through_model()

    product_util = factory.SubFactory(ProductUtilFactory)
    unique_selling_point = factory.SubFactory(UniqueSellingPointFactory)
