from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .exceptions import BrokerAccountCreationError

from .serializers import BrokerSerializer, BrokerAccountSerializer, DeleteBrokerAccountSerializer, GetBrokerAccountSerializer, PatchBrokerAccountSerializer, PostBrokerAccountSerializer
from .models import Broker

from qt_utils.responses import ApiMessageResponse


class Brokers(APIView):
    """
    The API for getting all Broker options
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BrokerSerializer

    def get(self, request):
        response_serializer = self.serializer_class(Broker.objects.all(), many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class BrokerAccountItem(APIView):
    """
    The API for creating, updating and deleting a BrokerAccount
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BrokerAccountSerializer

    def post(self, request):
        serializer = PostBrokerAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        broker_id = data.get("broker_id")
        authentication_method_id = data.get("authentication_method_id")
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        user = request.user

        # Ugly try/except piece, but necessary for preventing duplicate BrokerAccounts.
        # The custom UniqueConstraints wouldn't be catched by the transaction.atomic block otherwise.
        with transaction.atomic():
            try:
                user.create_broker_account(
                    broker_id,
                    authentication_method_id,
                    email,
                    username,
                    password,
                )
            except BrokerAccountCreationError as e:
                return ApiMessageResponse(
                    str(e),
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

        return ApiMessageResponse(
            _("Succesfully added Broker & checked connectivity"),
            status=status.HTTP_202_ACCEPTED,
        )

    def patch(self, request):
        serializer = PatchBrokerAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        broker_account_id = data.get('broker_account_id')
        authentication_method_id = data.get('authentication_method_id')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        with transaction.atomic():
            broker_account = user.update_broker_account_with_id(
                broker_account_id,
                authentication_method_id,
                email,
                username,
                password,
            )

        response_serializer = self.serializer_class(broker_account)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def get(self, request, broker_account_id):
        serializer = GetBrokerAccountSerializer(data={"broker_account_id": broker_account_id})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        broker_account_id = data.get('broker_account_id')

        broker_account = user.get_broker_account_by_id(broker_account_id)

        response_serializer = self.serializer_class(broker_account)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, broker_account_id):
        serializer = DeleteBrokerAccountSerializer(data={"broker_account_id": broker_account_id})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        broker_account_id = data.get('broker_account_id')

        with transaction.atomic():
            user.delete_broker_account_by_id(broker_account_id)

        return ApiMessageResponse(
            _("Succesfully deleted Broker Account."),
            status=status.HTTP_202_ACCEPTED,
        )


class BrokerAccounts(APIView):
    """
    The API for getting all BrokerAccounts
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BrokerAccountSerializer

    def get(self, request):
        user = request.user

        broker_accounts = user.get_all_broker_accounts()

        response_serializer = self.serializer_class(broker_accounts, many=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)