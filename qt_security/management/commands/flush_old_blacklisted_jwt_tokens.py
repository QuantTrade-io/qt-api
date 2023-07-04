from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import BlacklistedJWTToken


class Command(BaseCommand):
    help = "Flush old blacklisted JWT tokens"

    def handle(self, *args, **kwargs) -> None:
        # threshold = timezone.now() - timedelta(days=1)
        threshold = timezone.now() - timedelta(minutes=1)
        BlacklistedJWTToken.objects.filter(created_at__lt=threshold).delete()
