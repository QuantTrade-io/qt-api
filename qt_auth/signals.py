from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import User


@receiver(post_delete, sender=User)
def delete_user(sender, instance, *args, **kwargs):
    # Cancel subscription
    instance.cancel_current_subscription()
    # Delete AWS S3 folder for user (based on email)
    instance.delete_aws_resources_for_user()
