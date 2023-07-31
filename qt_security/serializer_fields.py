from datetime import datetime
from rest_framework.fields import Field


class CurrentField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super(CurrentField, self).__init__(**kwargs)

    def to_representation(self, device):
        current_token = self.context.get("current_token")
        return current_token == device.token.token


class ImageField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super(ImageField, self).__init__(**kwargs)

    def to_representation(self, device):
        return device.get_image


class DateField(Field):
    def __init__(self, source=None, **kwargs):
        super(DateField, self).__init__(source=source, **kwargs)

    def to_representation(self, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")
