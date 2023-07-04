from rest_framework.fields import Field


class IntervalField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super(IntervalField, self).__init__(**kwargs)

    def to_representation(self, price):
        return price.recurring["interval"]
