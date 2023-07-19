import magic
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


def validate_image_size_and_mime_type(image):
    # Check file size
    if image.size > settings.MAXIMUM_FILE_SIZE:
        raise ValidationError(_("File size exceeds the maximum limit of 10MB."))

    # Check MIME type
    try:
        mime_type = magic.from_buffer(image.read(), mime=True)
        if mime_type not in settings.SUPPORTED_MEDIA_MIMETYPES:
            raise ValidationError(
                _("Invalid image format. Only GIF, JPEG, and PNG are allowed.")
            )
    except Exception:
        raise ValidationError(
            _("Error while validating the image. Make sure it is a valid image file.")
        )

    # Reset file cursor back to the beginning so that it can be saved later
    image.seek(0)

    return image
