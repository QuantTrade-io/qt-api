from django.urls import path

from .views import Brokers, BrokerAccountItem, BrokerAccounts

brokers_urlpatterns = [
    path("", Brokers.as_view(), name="brokers"),
    path("account/", BrokerAccountItem.as_view(), name="broker-account"),
    path("account/<int:broker_account_id>/", BrokerAccountItem.as_view(), name="broker-account-item"),
    path("accounts/", BrokerAccounts.as_view(), name="broker-accounts"),
]
