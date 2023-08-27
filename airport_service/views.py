from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from airport_service.models import AirplaneType, Airplane
from airport_service.permissions import IsAdminOrIsAuthenticatedReadOnly
from airport_service.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneImageSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of strings to list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        airplane_types = self.request.query_params.get("airplane_types")

        if airplane_types:
            airplane_types_ids = self._params_to_ints(airplane_types)
            queryset = queryset.filter(airplane_type__id__in=airplane_types_ids)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("airplane_type")

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer

        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=self.request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "airplane_types",
    #             type={"type": "list", "items": {"type": "number"}},
    #             description="Filter by AirplaneTypes id(ex. ?airplane_types=1,3)"
    #         ),
    #     ]
    # )
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)
