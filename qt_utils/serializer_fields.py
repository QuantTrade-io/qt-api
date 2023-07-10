from rest_framework.fields import Field


class ImageField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super(ImageField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj.get_image
