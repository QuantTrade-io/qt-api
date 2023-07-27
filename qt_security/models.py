import requests
from django.conf import settings
from django.db import models
from django.db.models import Q
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from user_agents import parse

from qt_auth.models import User
from qt_utils.model_loaders import get_blacklisted_token_model
from qt_utils.models import AbstractTimeStampModel, QTPublicAssets


class BlacklistedJWTToken(AbstractTimeStampModel):
    """
    Model that holds a token that is issued by ourselves either for:
        - verify email
        - change email
        - change password
    If a token is used, it should be added to this model in order to make
    sure that a token is only used once.
    """

    token = models.CharField(max_length=1024, unique=True)

    class Meta:
        verbose_name = "Blacklisted JWT Token"
        verbose_name_plural = "Blacklisted JWT Tokens"

    def __str__(self):
        return self.token


class DeviceImage(AbstractTimeStampModel):
    """
    Model for matching device info with an image,
    in order to easily upload and update information.
    """

    image = models.ImageField(
        upload_to="images/devices/",
        blank=True,
        null=True,
        storage=QTPublicAssets(),
        max_length=250,
    )
    description = models.TextField(max_length=1024)

    def __str__(self):
        return self.description

    @property
    def get_url(self):
        if self.image:
            return self.image.url.split("?")[0]


# Create your models here.
class Device(AbstractTimeStampModel):
    """
    Model that holds information regarding the Device that has
    issued a refresh token or used the refresh token
    """

    # this is a different token than the BlacklistedJWTToken
    user = models.ForeignKey(User, related_name="devices", on_delete=models.CASCADE)
    image = models.ForeignKey(DeviceImage, on_delete=models.SET_NULL, null=True)
    info = models.CharField(max_length=255)

    class Meta:
        unique_together = [["image", "info"]]

    def __str__(self):
        return self.info

    def save(self, *args, **kwargs):
        self.image = self._get_device_image(self.info)
        super().save(*args, **kwargs)

    @property
    def get_image(self):
        if self.image:
            return self.image.get_url

    @classmethod
    def get_information_from_request(cls, request):
        info = cls._get_device_info(request.META.get("HTTP_USER_AGENT"))
        image = cls._get_device_image(info)

        return info, image

    @classmethod
    def _get_device_info(cls, user_agent):
        if not user_agent:
            return "Other / Other / Other"
        return str(parse(user_agent))

    @classmethod
    def _get_device_image(cls, info):
        parts = info.split("/")
        words = [part.strip() for part in parts]
        search_items = [item.split()[0] for item in reversed(words)]

        # iterate over words starting from the most important one (first word)
        for word in search_items:
            device_image = DeviceImage.objects.filter(
                Q(description__icontains=word)
            ).first()
            if not device_image:
                continue
            return device_image
        return None


class Session(AbstractTimeStampModel):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="sessions"
    )
    token = models.OneToOneField(
        OutstandingToken, related_name="session", on_delete=models.CASCADE
    )
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"Session {self.id} for {self.device.info}"

    @property
    def active(self):
        # check if there is a blacklisted token related to this device token
        if hasattr(self.token, "blacklistedtoken"):
            return False
        return True

    @classmethod
    def create_session(cls, device, token, city, country):
        session = cls.objects.create(
            device=device,
            token=token,
            city=city,
            country=country,
        )

        return session

    @classmethod
    def get_information_from_request(cls, request):
        ip_address = cls._get_ip_from_request(request)
        city, country = cls._get_location_from_ip(ip_address)

        return city, country

    @classmethod
    def _get_ip_from_request(cls, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[-1].strip()
        elif request.META.get("HTTP_X_REAL_IP"):
            ip = request.META.get("HTTP_X_REAL_IP")
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @classmethod
    def _get_location_from_ip(cls, ip_address):
        response = requests.get(
            f"https://api.ipgeolocation.io/ipgeo?"
            f"apiKey={settings.GEOLOCATION_API_KEY}&"
            f"ip={ip_address}"
        )
        parsed_response = response.json()

        return parsed_response["city"], parsed_response["country_name"]

    def blacklist_token(self):
        BlacklistedToken = get_blacklisted_token_model()
        _, _ = BlacklistedToken.objects.get_or_create(token=self.token)
