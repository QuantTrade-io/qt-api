from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from qt_utils.responses import ApiMessageResponse

from .serializers import (
    DeleteDeviceItemSerializer,
    DevicesSerializer,
    GetDeviceSerializer,
)


class Devices(APIView):
    """
    The API for retrieving all the logged in Devices at once
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DevicesSerializer

    def get(self, request):
        query_params = request.query_params.dict()
        serializer = GetDeviceSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        current_token = data.get("refresh_token")
        user = request.user
        response_serializer = self.serializer_class(
            user.get_devices(), context={"current_token": current_token}, many=True
        )

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class DeviceItem(APIView):
    """
    The API for deleting a single Device
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DeleteDeviceItemSerializer

    def delete(self, request, device_id):
        # this is not a real delete, but rather a Blacklist
        request_data = self._get_request_data(request, device_id)
        serializer = DeleteDeviceItemSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        return self.valid_request_data(serializer.validated_data, request)

    def valid_request_data(self, data, request):
        device_id = data.get("device_id")
        user = request.user

        with transaction.atomic():
            user.blacklist_token_by_device_id(device_id)

        return ApiMessageResponse(
            _(
                """
                Device succesfully deleted form the logged in list,
                it could take a couple of minutes
                before the changes are affected on the device itself.
                """
            ),
            status=status.HTTP_202_ACCEPTED,
        )

    def _get_request_data(self, request, device_id):
        request_data = request.data.copy()
        request_data["device_id"] = device_id
        return request_data
