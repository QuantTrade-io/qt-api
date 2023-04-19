from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory

from qt_utils.model_loaders import get_user_model

from faker import Faker

fake = Faker()


class UserRegisterFactory(DjangoModelFactory):
    """
    Creates a default user with all relevant properties.
    """

    class Meta:
        model = get_user_model()

    email = fake.email()
    password = make_password(fake.password())
    first_name = fake.first_name()
    last_name = fake.last_name()
    are_guidelines_accepted = True
    is_email_verified = False

class UserEmailVerifiedFactory(UserRegisterFactory):
    is_email_verified = True
