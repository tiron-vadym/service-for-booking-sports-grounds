from django.urls import path, include
from rest_framework import routers

from service.views import (
    SportGroundViewSet,
    ReservationViewSet,
    PaymentViewSet
)

router = routers.DefaultRouter()
router.register("sports-grounds", SportGroundViewSet)
router.register("reservations", ReservationViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "service"
