from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from qt_utils.model_loaders import get_session_model
from qt_utils.responses import ApiMessageResponse

from .serializers import (
    DeleteSessionItemSerializer,
    DeviceSerializer,
    GetDeviceSerializer,
)


class Devices(APIView):
    """
    The API for retrieving all the logged in Devices at once
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceSerializer

    def get(self, request):
        query_params = request.query_params.dict()
        serializer = GetDeviceSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        current_token = data.get("refresh_token")
        user = request.user
        response_serializer = self.serializer_class(
            user.get_current_devices_and_session(),
            context={"current_token": current_token},
            many=True,
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class SessionItem(APIView):
    """
    The API for blacklisting a single Session
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DeleteSessionItemSerializer

    def delete(self, request, session_id):
        # this is not a real delete, but rather a Blacklist
        request_data = self._get_request_data(request, session_id)
        serializer = self.serializer_class(data=request_data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        session_id = data.get("session_id")

        Session = get_session_model()
        session = Session.objects.get(pk=session_id)

        with transaction.atomic():
            session.blacklist_token()

        return ApiMessageResponse(
            _(
                """
                Session succesfully deleted form the logged in list,
                it could take a couple of minutes
                before the changes are affected on the device itself.
                """
            ),
            status=status.HTTP_202_ACCEPTED,
        )

    def _get_request_data(self, request, session_id):
        request_data = request.data.copy()
        request_data["session_id"] = session_id
        return request_data
