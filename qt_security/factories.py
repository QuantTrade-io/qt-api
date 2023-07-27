from factory import Faker
from factory.django import DjangoModelFactory

from qt_utils.model_loaders import get_device_model, get_session_model


class DeviceFactory(DjangoModelFactory):
    """
    Creates a Device and some info.
    """

    class Meta:
        model = get_device_model()

    user = None
    image = None
    info = Faker("sentence")


class SessionFactory(DjangoModelFactory):
    """
    Creates a session.
    """

    class Meta:
        model = get_session_model()

    token = None
    device = None
    city = Faker("city")
    country = Faker("country")
