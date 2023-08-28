from django.db.models import F, Count, Prefetch
from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from airport_service.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Ticket, Order,
)
from airport_service.permissions import IsAdminOrIsAuthenticatedReadOnly
from airport_service.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneImageSerializer,
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    TicketSerializer,
    TicketListSerializer, OrderListSerializer, OrderSerializer,
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
            queryset = queryset.select_related("airplane_type")

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_types",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by AirplaneTypes id(ex. ?airplane_types=1,3)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("destination", "source")

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(route__source__closest_big_city__iexact=source)

        if destination:
            queryset = queryset.filter(
                route__destination__closest_big_city__iexact=destination
            )

        if self.action == "list":
            queryset = queryset.select_related(
                "airplane", "route__destination", "route__source"
            ).annotate(
                tickets_available=(F("airplane__rows") * F("airplane__seats_in_row"))
                - Count("tickets")
            )
            return queryset

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "airplane", "route__source", "route__destination"
            ).prefetch_related("tickets", "crew")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=str,
                description="Filter by Airport(source) closest big city(ex. ?source=shenzhen)",
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description=(
                        "Filter by Airport(destination) closest big city(ex. ?destination=beijing)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "flight__route__source", "flight__route__destination", "flight__airplane"
            )
            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer

        return TicketSerializer


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size'"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__flight__airplane",
                "tickets__flight__route__source",
                "tickets__flight__route__destination"
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
