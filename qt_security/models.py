import requests
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from user_agents import parse

from qt_auth.models import User
from qt_utils.models import AbstractTimeStampModel


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


# Create your models here.
class Device(AbstractTimeStampModel):
    """
    Model that holds information regarding the Device that has
    issued a refresh token or used the refresh token
    """

    # different token than the BlacklistedJWTToken
    user = models.ForeignKey(User, related_name="devices", on_delete=models.CASCADE)
    token = models.OneToOneField(
        OutstandingToken, related_name="device", on_delete=models.CASCADE
    )
    os = models.CharField(_("Operating System"), max_length=255)
    family = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.os} | {self.name}"

    # TODO: make the images work
    # @property
    # def image(self):
    #     # TODO
    #     if self.name != "Other":
    #         return "Name"
    #     if self.family != "Other":
    #         return "Family"
    #     if self.os != "Other":
    #         return "OS"
    #     return "Unknown"

    @classmethod
    def create_device(cls, user, token, os, family, name, city, country):
        device = cls.objects.create(
            user=user,
            token=token,
            os=os,
            family=family,
            name=name,
            city=city,
            country=country,
        )

        return device

    @classmethod
    def get_information_from_request(cls, request):
        ip_address = cls._get_ip_from_request(request)
        os, family, name = cls._get_device_name_and_type(
            request.META.get("HTTP_USER_AGENT")
        )
        city, country = cls._get_location_from_ip(ip_address)

        return os, family, name, city, country

    @classmethod
    def _get_location_from_ip(cls, ip_address):
        response = requests.get(
            f"https://api.ipgeolocation.io/ipgeo?"
            f"apiKey={settings.GEOLOCATION_API_KEY}&"
            f"ip={ip_address}"
        )
        parsed_response = response.json()

        return parsed_response["city"], parsed_response["country_name"]

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
    def _get_device_name_and_type(cls, user_agent):
        if not user_agent:
            return "Other", "Other", "Other"
        user_agent = parse(user_agent)
        os = family = name = "Unknown"
        if user_agent.os.family != "Other":
            os = user_agent.os.family
        if user_agent.browser.family != "Other":
            family = user_agent.browser.family
        if user_agent.device.family != "Other":
            name = user_agent.device.family

        return os, family, name
