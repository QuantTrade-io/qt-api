# This is the template for your own settings_local.py file.
# In order to make the development server running locally,
# you need to copy and paste the content of this file
# to a newly created file named; settings_local.py
# Within the settings_local.py file,
# you can adjust the settings according to your needs.

from .settings_base import *  # noqa

# AWS config
AWS_DEFAULT_REGION = ""
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

AWS_S3_PUBLIC_ASSETS = ""
AWS_S3_PRIVATE_ASSETS = ""

AWS_S3_ACCESS_KEY_ID = ""
AWS_S3_SECRET_ACCESS_KEY = ""

# Email config
AWS_SES_REGION_NAME = ""
AWS_SES_REGION_ENDPOINT = ""

AWS_SES_ACCESS_KEY_ID = ""
AWS_SES_SECRET_ACCESS_KEY = ""

INFO_EMAIL_ADDRESS = ""
NO_REPLY_EMAIL_ADDRESS = ""

# Local Stripe settings
STRIPE_TEST_SECRET_KEY = ""
STRIPE_SECRET_KEY = STRIPE_TEST_SECRET_KEY
DJSTRIPE_WEBHOOK_SECRET = ""

# Geolocation API
GEOLOCATION_API_KEY = ""

WWW_URL = "localhost:8000"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db-name",
        "USER": "db-user",
        "PASSWORD": "db-password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
