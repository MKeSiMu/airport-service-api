from django.urls import path, include
from rest_framework import routers

from airport_service.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport-service"
