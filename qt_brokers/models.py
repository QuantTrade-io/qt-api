from django.utils.translation import gettext_lazy as _
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Q

from qt_auth.models import User
from .exceptions import BrokerAccountCreationError
from qt_utils.models import QTPublicAssets

from encrypted_model_fields.fields import EncryptedCharField, EncryptedIntegerField

from brohub.broker import AuthenticationMethods, authenticate, logout
from brohub.brokers import Brokers


class BrokerAuthenticationMethod(models.Model):
    method = models.CharField(
        max_length=128,
        choices=AuthenticationMethods.choices(),
        unique=True
    )

    def __str__(self):
        return self.method


class Broker(models.Model):
    name = models.CharField(choices=Brokers.choices(), max_length=128)
    image = models.ImageField(
        upload_to="images/broker-information/",
        blank=True,
        null=True,
        storage=QTPublicAssets(),
        max_length=250,
    )
    authentication_methods = models.ManyToManyField(BrokerAuthenticationMethod, related_name="brokers")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_broker')
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def get_image(self):
        if self.image:
            return self.image.url.split("?")[0]


class BrokerAccount(models.Model):
    user = models.ForeignKey(User, related_name='broker_accounts', on_delete=models.CASCADE)

    # information regarding the broker & authentication
    broker = models.ForeignKey(Broker, related_name="broker_account", on_delete=models.CASCADE)
    authentication_method = models.ForeignKey(BrokerAuthenticationMethod, related_name="authentication_method", on_delete=models.CASCADE)

    # Fields that need to be included in the authentication function
    # will be unpacked as **kwargs  & validated in qt_brohub
    # encrypted for security reasons
    email = models.EmailField(_("email address"), blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = EncryptedCharField(blank=True, null=True)

    # degiro specific; needs to be included as well
    int_account = EncryptedIntegerField(blank=True, null=True)

    broker_connection = None

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['broker', 'authentication_method', 'username'], name='unique_broker_account_username', condition=Q(username__isnull=False)),
            models.UniqueConstraint(fields=['broker', 'authentication_method', 'email'], name='unique_broker_account_emailt', condition=Q(email__isnull=False))
        ]

    def __str__(self):
        return f"{self.user} | {self.broker.name} | {self.authentication_method}"

    @classmethod
    def create_broker_account(cls, user_id, broker_id, authentication_method_id, email, username, password, **kwargs):
        broker_account, created = cls.objects.get_or_create(
            user_id=user_id, broker_id=broker_id, authentication_method_id=authentication_method_id, email=email, username=username
        )

        if not created:
            # raise custom exception with an error message
            raise BrokerAccountCreationError(_("Broker account with the provided credentials already exists."))
        
        broker_account.update(password=password, **kwargs)
        return broker_account

    def update(self,  **kwargs):
        for key, value in kwargs.items():
            # check if the attribute/key exists in the model
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise FieldError(f"'{key}' is not a valid field for {self.__class__.__name__}.")

        self.save()
    
    def open_broker_connection(self):
        self.broker_connection = authenticate(self.broker.name, self.auth_method, email=self.email, username=self.username, password=self.password, int_account=self.int_account)
        # store int_account if broker is Brokers.DEGIRO
        if self.broker.name == Brokers.DEGIRO and not self.int_account:
            self.int_account = self.broker_connection.int_account
            self.save()
    
    def close_broker_connection(self):
        logout(self.broker_connection, self.authentication_method)

    def update_holdings(self):
        # create, update or delete holdings
        broker_connection = self.open_broker_connection()
        current_holdings = broker_connection.get_current_holdings()


class Holding(models.Model):
    # ID that is internally known by the broker
    internal_id = models.CharField(max_length=255)
    isin = models.CharField(max_length=128)
    account = models.ForeignKey(BrokerAccount, related_name="holdings", on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    ticker = models.CharField(max_length=128)
    ticker_suffix = models.CharField(max_length=128)
    exchange_id = models.CharField(max_length=128, blank=True, null=True)
    exchange_name = models.CharField(max_length=128, blank=True, null=True)
    exchange_city = models.CharField(max_length=128, blank=True, null=True)
    exchange_country = models.CharField(max_length=128, blank=True, null=True)
    currency = models.CharField(max_length=5)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class CashPosition(models.Model):
    # TODO: implemet cash positions
    pass