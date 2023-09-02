import os
import django

from celery import Celery


environment = os.environ.get("ENVIRONMENT")
if environment:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"qt.settings_{environment}")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qt.settings_local")

# Setup django project
django.setup()

app = Celery('qt')

# Use the string 'django.conf:settings' to load settings from Django's settings.py:
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()