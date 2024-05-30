from django.urls import path, include
from rest_framework import routers

from service.views import (
    SportGroundViewSet,
    SportFieldViewSet,
    BookingViewSet,
    PaymentViewSet
)

router = routers.DefaultRouter()
router.register("sports-grounds", SportGroundViewSet)
router.register("sports-fields", SportFieldViewSet)
router.register("bookings", BookingViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "service"
