from factory.django import DjangoModelFactory
from faker import Faker

from qt_utils.model_loaders import get_newsletter_subscriber_model

fake = Faker()


class NewsletterSubscriberFactory(DjangoModelFactory):
    """
    Create a Newsletter Subscriber.
    """

    class Meta:
        model = get_newsletter_subscriber_model()

    email = fake.email()
