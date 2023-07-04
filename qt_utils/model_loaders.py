from django.apps import apps


# AUTH
def get_user_model():
    return apps.get_model("qt_auth.User")


# BILLING
def get_product_util_model():
    return apps.get_model("qt_billing.ProductUtil")


def get_unique_selling_point_model():
    return apps.get_model("qt_billing.UniqueSellingPoint")


def get_unique_selling_point_model_through_model():
    return apps.get_model("qt_billing.ProductUniqueSellingPointThroughModel")


# SECURITY
def get_blacklisted_jwt_token_model():
    return apps.get_model("qt_security.BlacklistedJWTToken")


def get_device_model():
    return apps.get_model("qt_security.Device")


# UTILS
def get_newsletter_subscriber_model():
    return apps.get_model("qt_utils.NewsletterSubscriber")


# DJ STRIPE
def get_stripe_customer_model():
    return apps.get_model("djstripe.Customer")


def get_stripe_subscription_model():
    return apps.get_model("djstripe.Subscription")


def get_stripe_product_model():
    return apps.get_model("djstripe.Product")


def get_stripe_plan_model():
    return apps.get_model("djstripe.Plan")


def get_stripe_price_model():
    return apps.get_model("djstripe.Price")


# DJANGORESTFRAMEWORK-SIMPLEJWT
def get_outstanding_token_model():
    return apps.get_model("token_blacklist.OutstandingToken")


def get_blacklisted_token_model():
    return apps.get_model("token_blacklist.BlacklistedToken")
