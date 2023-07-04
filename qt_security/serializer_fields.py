from rest_framework.fields import Field


class CurrentField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super(CurrentField, self).__init__(**kwargs)

    def to_representation(self, device):
        current_token = self.context.get("current_token")
        return current_token == device.token.token
