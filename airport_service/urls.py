from django.urls import path, include
from rest_framework import routers

from airport_service.views import AirplaneTypeViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport-service"
