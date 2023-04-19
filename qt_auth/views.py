from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from qt_utils.model_loaders import get_user_model

from .serializers import LoginSerializer, RegisterSerializer


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
            new_user.save()

        with transaction.atomic():
            new_user.create_stripe_account()
            new_user.save()

        new_user.send_email_verification()

        return Response(_("Account succesfully registered"), status=status.HTTP_201_CREATED)


# class EmailVerify(APIView):
#     """
#     The API to verify if a email is valid.
#     """
#     serializer_class = EmailVerifySerializer
#
#     def post(self, request):
#         user = request.user
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         token = serializer.validated_data.get('token')
#
#         user.verify_email_with_token(token)
#
#         return ApiMessageResponse(_('Email verified'), status=status.HTTP_200_OK)
#

class Subscription(APIView):
    pass


class Login(APIView):
    """
    The API to login a user.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        email = data["email"]
        password = data["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            # token = user.generate_token()
            token = user.get_jwt_token()
            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            raise AuthenticationFailed()
