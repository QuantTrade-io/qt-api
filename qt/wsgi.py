"""
WSGI config for qt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

environment = os.environ.get("ENVIRONMENT")
if environment:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"qt.settings_{environment}")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qt.settings_local")

application = get_wsgi_application()
