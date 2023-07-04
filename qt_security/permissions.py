from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class HasValidSubscription(BasePermission):
    """
    Dont allow access to users without a valid subscription
    """

    def has_permission(self, request, view):
        user = request.user
        return check_user_has_valid_subscription(user=user)


def check_user_has_valid_subscription(user):
    if not user.has_valid_subscription():
        raise PermissionDenied(
            _("Your account is not associated with a valid subscription.")
        )
    return True
