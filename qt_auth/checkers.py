from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

from brohub.broker import AuthenticationMethods, authenticate, logout
from brohub.brokers import Brokers

from qt_utils.model_loaders import get_broker_authentication_method_model, get_broker_model, get_broker_account_model


def check_can_connect_with_broker(broker_id, authentication_method_id, email, username, password):
    Broker = get_broker_model()
    broker = Broker.objects.get(pk=broker_id)

    BrokerAuthenticationMethod = get_broker_authentication_method_model()
    broker_authentication_method = BrokerAuthenticationMethod.objects.get(pk=authentication_method_id)

    try:
        broker_connection = authenticate(Brokers(broker.name), AuthenticationMethods(broker_authentication_method.method), email=email, username=username, password=password)
    except ConnectionError as e:
        raise AuthenticationFailed(detail=_(
            f"""
            Unable to connect with broker {broker.name},
            {e}
            """
        ))
    
    logout(broker_connection, AuthenticationMethods(broker_authentication_method.method))
    return {
        "int_account": broker_connection.int_account,
    }
