from django.urls import path

from .views import (
    AuthenticatedUser,
    Login,
    LoginRefreshToken,
    Logout,
    Register,
    RequestResetEmail,
    RequestResetPassword,
    RequestVerifyEmail,
    VerifyEmail,
    VerifyResetEmail,
    VerifyResetPassword,
)

auth_urlpatterns = [
    # Un-Authenticated User API endpoints
    path("user-register/", Register.as_view(), name="user-register"),
    path("user-register/verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path(
        "user-register/request-verify-email/",
        RequestVerifyEmail.as_view(),
        name="request-verify-email",
    ),
    path("user-login/", Login.as_view(), name="user-login"),
    path("refresh-token/", LoginRefreshToken.as_view(), name="refresh-token"),
    path("logout/", Logout.as_view(), name="user-logout"),
    path("reset/email/", RequestResetEmail.as_view(), name="reset-email"),
    path("reset/password/", RequestResetPassword.as_view(), name="reset-password"),
    path("verify/reset-email/", VerifyResetEmail.as_view(), name="verify-reset-email"),
    path(
        "verify/reset-password/",
        VerifyResetPassword.as_view(),
        name="verify-reset-password",
    ),
    # Authenticated User API endpoints
    path("user/", AuthenticatedUser.as_view(), name="authenticated-user"),
    # path(
    #   "user/change-subscription/",
    #   AuthenticatedUserChangeSubscription.as_view(),
    #   name="authenticated-user-change-subscription"
    # ),
    # path(
    #   "user/delete/",
    #   AuthenticatedUserDelete.as_view(),
    #   name="authenticated-user-delete"
    # ),
]
