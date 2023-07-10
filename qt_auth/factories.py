import stripe
from django.conf import settings
from django.contrib.auth.hashers import make_password
from factory import Faker
from factory.django import DjangoModelFactory

from qt_utils.model_loaders import (
    get_stripe_customer_model,
    get_stripe_subscription_model,
    get_user_model,
)


class UserFactory(DjangoModelFactory):
    """
    Creates a default user with all relevant properties.
    """

    class Meta:
        model = get_user_model()

    email = Faker("email")
    password = make_password("AhhYeahWakeupYeah")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    status = get_user_model().STATUS_TYPE_REGISTERED
    are_guidelines_accepted = True
    is_email_verified = True


class UserUnsubscribedFactory(UserFactory):
    """
    UserFactory + Stripe Customer.
    NOTE: User only when needed, slows down the test cases.
    """

    status = get_user_model().STATUS_TYPE_VERIFIED

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create to add a Stripe customer to the user"""
        user = super()._create(model_class, *args, **kwargs)

        Customer = get_stripe_customer_model()
        stripe_customer = stripe.Customer.retrieve(
            settings.STRIPE_UNSUBSCRIBED_CUSTOMER_ID
        )
        djstripe_customer = Customer.sync_from_stripe_data(stripe_customer)
        user.customer = djstripe_customer

        user.save()

        return user


class UserSubscribedFactory(UserFactory):
    """
    UserFactory + Stripe Customer + Stripe Subscription.
    NOTE: Use only when needed, slows down the test cases.
    """

    status = get_user_model().STATUS_TYPE_VERIFIED

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create to add a Stripe customer to the user"""
        user = super()._create(model_class, *args, **kwargs)

        Customer = get_stripe_customer_model()
        stripe_customer = stripe.Customer.retrieve(
            settings.STRIPE_SUBSCRIBED_CUSTOMER_ID
        )
        djstripe_customer = Customer.sync_from_stripe_data(stripe_customer)

        user.customer = djstripe_customer

        Subscription = get_stripe_subscription_model()
        stripe_subscription = stripe.Subscription.retrieve(
            settings.STRIPE_SUBSCRIPTION_ITEM_ID
        )
        Subscription.sync_from_stripe_data(stripe_subscription)

        user.save()
        return user
