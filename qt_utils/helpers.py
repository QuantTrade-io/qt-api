from io import BytesIO

import boto3
from django.conf import settings
from django.core.files import File
from PIL import Image

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def aws_instance_directory_path(instance, filename):
    # file will be uploaded to /user_<id>/<filename>
    return "user_{0}/{1}".format(instance.email, filename)


def get_s3_image(bucket_name, key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_data = response["Body"].read()
    image = Image.open(BytesIO(image_data))

    # Save the PIL Image to a BytesIO object
    img_io = BytesIO()
    image.save(img_io, format=image.format)
    return File(img_io, name="profile_image.png")
