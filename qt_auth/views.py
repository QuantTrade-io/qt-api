from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from qt_security.permissions import HasValidSubscription
from qt_utils.model_loaders import (
    get_device_model,
    get_outstanding_token_model,
    get_user_model,
)
from qt_utils.responses import ApiMessageResponse

from .serializers import (
    GetAuthenticatedUserSerializer,
    LoginRefreshTokenSerializer,
    LoginSerializer,
    LogoutSerializer,
    PatchAuthenticatedUserSerializer,
    PatchAuthenticatedUserSettingsSerializer,
    RegisterSerializer,
    RequestResetPasswordSerializer,
    RequestVerifyEmailSerializer,
    VerifyEmailSerializer,
    VerifyResetEmailSerializer,
    VerifyResetPasswordSerializer,
)


class Register(APIView):
    """
    The API to register an account.
    """

    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        password = data.get("password")
        are_guidelines_accepted = data.get("are_guidelines_accepted")

        User = get_user_model()

        new_user = User.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            are_guidelines_accepted=are_guidelines_accepted,
        )

        with transaction.atomic():
            new_user.create_stripe_account()
            new_user.save()

            new_user.send_email_verification_mail()

        return ApiMessageResponse(
            _(
                """
                Account succesfully registered,
                please check your email in order to proceed.
                """
            ),
            status=status.HTTP_201_CREATED,
        )


class VerifyEmail(APIView):
    """
    The API to verify if a users email.
    """

    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        token = data.get("token")

        User = get_user_model()

        user = User.get_user_for_token(token, User.JWT_TOKEN_TYPE_VERIFY_EMAIL)

        if user.status not in [
            User.STATUS_TYPE_REGISTERED,
            User.STATUS_TYPE_CHANGE_EMAIL,
        ]:
            return ApiMessageResponse(
                _("Unable to verify email in the current status."),
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        with transaction.atomic():
            user.set_user_status_email_verified()
            user.save()

        return ApiMessageResponse(
            _("Account succesfully verified, welcome to the Team."),
            status=status.HTTP_202_ACCEPTED,
        )


class RequestVerifyEmail(APIView):
    """
    The API to (re)request the email verification
    """

    serializer_class = RequestVerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        email = data.get("email")

        User = get_user_model()
        user = User.get_user_with_email(email)

        if user.status not in [
            User.STATUS_TYPE_REGISTERED,
            User.STATUS_TYPE_CHANGE_EMAIL,
        ]:
            return ApiMessageResponse(
                _("Your email is already verified, you should be able to login."),
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        with transaction.atomic():
            user.send_request_email_verification_mail()

        return ApiMessageResponse(
            _(
                """
                A new email is send to you,
                please check the instructions in order to proceed.
                """
            ),
            status=status.HTTP_200_OK,
        )


class Login(APIView):
    """
    The API to login a user.
    """

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        email = data["email"]
        password = data["password"]
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed()

        User = get_user_model()

        if not user.status == User.STATUS_TYPE_VERIFIED:
            return Response(
                {"account_status": user.status}, status=status.HTTP_401_UNAUTHORIZED
            )

        token = user.get_jwt_token()

        # Save user request information
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=token["refresh"])

        Device = get_device_model()
        info, city, country = Device.get_information_from_request(request)

        with transaction.atomic():
            Device.create_device(user, outstanding_token, info, city, country)

        return Response(
            {
                "token": token,
                "account_status": user.status,
                "subscribed": user.has_valid_subscription(),
            },
            status=status.HTTP_200_OK,
        )


class LoginRefreshToken(APIView):
    """
    The API for logging in via the refresh token
    """

    serializer_class = LoginRefreshTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        refresh_token = data["refresh_token"]

        User = get_user_model()

        token = User.get_access_token_for_refresh_token(refresh_token)
        user = User.objects.get(pk=token["user_id"])

        if not token or not user:
            return Response(
                _("Unable to login with given credentials"),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.status == User.STATUS_TYPE_VERIFIED:
            return Response(
                {"account_status": user.status}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Update user request information
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=refresh_token)

        Device = get_device_model()
        device = Device.objects.get(token=outstanding_token)
        __, city, country = Device.get_information_from_request(request)

        with transaction.atomic():
            device.city = city
            device.country = country
            device.updated_at = timezone.now()
            device.save()

        return Response(
            {
                "access_token": str(token.access_token),
                "account_status": user.status,
                "subscribed": user.has_valid_subscription(),
                "image": user.get_image,
            },
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    """
    The API for logging out a user -> blacklisting tokens
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        refresh_token = data["refresh_token"]
        user = request.user

        with transaction.atomic():
            user.blacklist_token(refresh_token)

        return ApiMessageResponse(
            _("Logged out succesfully"), status=status.HTTP_200_OK
        )


class RequestResetPassword(APIView):
    """
    The API for requesting and verifying a password reset
    """

    serializer_class = RequestResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        email = data.get("email")

        User = get_user_model()
        user = User.get_user_with_email(email)

        with transaction.atomic():
            user.send_password_reset_mail()

        return ApiMessageResponse(
            _(
                """
                Password reset email succesfully requested,
                please check your email in order to proceed.
                """
            ),
            status=status.HTTP_200_OK,
        )


class VerifyResetPassword(APIView):
    """
    The API for verifying the password reset
    """

    serializer_class = VerifyResetPasswordSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        token = data.get("token")
        password = data.get("password")

        User = get_user_model()

        user = User.get_user_for_token(token, User.JWT_TOKEN_TYPE_RESET_PASSWORD)

        with transaction.atomic():
            user.update_password(password)
            user.save()

        return ApiMessageResponse(
            _(
                """
                Password changed successfully,
                you'll be logged-out across all devices within a couple of minutes.
                """
            ),
            status=status.HTTP_202_ACCEPTED,
        )


class RequestResetEmail(APIView):
    """
    The API for requesting an email reset (change email)
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        with transaction.atomic():
            request.user.send_email_reset_mail()

        return ApiMessageResponse(
            _(
                """
                Change emailaddress succesfully requested,
                please check your current email in order to proceed.
                """
            ),
            status=status.HTTP_200_OK,
        )


class VerifyResetEmail(APIView):
    """
    The API for requesting an email reset (change email)
    """

    serializer_class = VerifyResetEmailSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        token = data.get("token")
        email_old = data.get("email_old")
        email_new = data.get("email_new")

        User = get_user_model()

        user_for_token = User.get_user_for_token(token, User.JWT_TOKEN_TYPE_RESET_EMAIL)
        user_for_email = User.get_user_with_email(email_old)

        # if the token for this user does not match with the email provided by the user
        # we can't change the email of the user and will decline the request
        if user_for_token != user_for_email:
            return ApiMessageResponse(
                _("Unable to match the current token with the email address provided."),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        with transaction.atomic():
            user_for_token.email = email_new
            user_for_token.set_user_status_change_email()
            user_for_token.save()
            user_for_token.blacklist_all_outstanding_tokens()
            user_for_token.send_email_reset_verification_mail()

        return ApiMessageResponse(
            _(
                """
                Email changed successfully,
                please check your new emails inbox in order to confirm.
                """
            ),
            status=status.HTTP_202_ACCEPTED,
        )


class AuthenticatedUser(APIView):
    """
    The API for retrieving all user settings & information
    """

    permission_classes = (
        IsAuthenticated,
        HasValidSubscription,
    )

    def get(self, request):
        user_serializer = GetAuthenticatedUserSerializer(request.user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = PatchAuthenticatedUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        with transaction.atomic():
            user.update(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                image=request.FILES.get("image"),
            )

            user.save()

        user_serializer = GetAuthenticatedUserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        #  stop stripe subscription
        user.cancel_current_subscription()
        #  delete user & corresponding objects
        user.delete()

        return ApiMessageResponse(
            _("Goodbye!"),
            status=status.HTTP_202_ACCEPTED,
        )


class AuthenticatedUserSettings(APIView):
    """
    The API for updating all user settings & information
    """

    permission_classes = (
        IsAuthenticated,
        HasValidSubscription,
    )

    def patch(self, request):
        serializer = PatchAuthenticatedUserSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        password_old = data.get("password_old")
        password_new = data.get("password_new")

        user = request.user

        if not user.check_password(password_old):
            raise AuthenticationFailed(detail=_("Password is not valid"))

        with transaction.atomic():
            user.update_password(password_new)
            user.save()

        return ApiMessageResponse(
            _(
                """
                Password changed successfully,
                you'll be logged-out across all devices within a couple of minutes.
                """
            ),
            status=status.HTTP_202_ACCEPTED,
        )
