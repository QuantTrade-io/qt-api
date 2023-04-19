# This is the template for your own settings_local.py file.
# In order to make the development server running locally,
# you need to copy and paste the content of this file to a newly created file named; settings_local.py
# Within the settings_local.py file, you can adjust the settings according to your needs.

from .settings_base import *

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
