import jwt
import stripe

from qt_security.factories import DeviceFactory, SessionFactory
from qt_utils.model_loaders import get_outstanding_token_model, get_user_model


def clear_stripe_customers():
    """
    Clear stripe customers on Unit Tests
    """
    User = get_user_model()
    users = User.objects.filter(customer__isnull=False)

    for user in users:
        stripe.Customer.delete(user.customer.id)


def generate_jwt_token(token_type, user_id, exp_time, secret_key):
    return jwt.encode(
        {"type": token_type, "user_id": user_id, "exp": exp_time},
        secret_key,
        algorithm="HS256",
    )


def make_authentication_headers_auth_token(user):
    token = user.get_jwt_token()

    # Create corresponding Device with this token
    OutstandingToken = get_outstanding_token_model()
    outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
    device = DeviceFactory(user=user)
    SessionFactory(device=device, token=outstanding_token)

    return {"HTTP_AUTHORIZATION": f"Bearer {token['access']}"}


def get_refresh_token_for_user(user):
    token = user.get_jwt_token()

    # Create corresponding Device with this token
    OutstandingToken = get_outstanding_token_model()
    outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
    device = DeviceFactory(user=user)
    SessionFactory(device=device, token=outstanding_token)

    return token["refresh"]
