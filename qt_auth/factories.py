from django.contrib.auth.hashers import make_password
from factory import Faker
from factory.django import DjangoModelFactory

from qt_utils.model_loaders import get_user_model


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
