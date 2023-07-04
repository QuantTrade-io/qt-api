import os

from .settings_base import *  # noqa

STRIPE_LIVE_SECRET_KEY = os.environ.get("STRIPE_LIVE_SECRET_KEY")
STRIPE_SECRET_KEY = STRIPE_LIVE_SECRET_KEY
