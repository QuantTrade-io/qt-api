from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import User


@receiver(post_delete, sender=User)
def delete_profile(sender, instance, *args, **kwargs):
    # Cancel subscription
    instance.cancel_current_subscription()
