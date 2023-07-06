from factory import Faker
from factory.django import DjangoModelFactory

from qt_utils.model_loaders import get_device_model


class DeviceFactory(DjangoModelFactory):
    """
    Creates a default user with all relevant properties.
    """

    class Meta:
        model = get_device_model()

    user = None
    token = None
    image = None
    info = Faker("sentence")
    city = Faker("city")
    country = Faker("country")
