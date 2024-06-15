from django.urls import path, include
from rest_framework import routers

from service.views import (
    SportsComplexViewSet,
    SportsFieldViewSet,
    BookingViewSet,
    PaymentViewSet
)

router = routers.DefaultRouter()
router.register("sports-complexes", SportsComplexViewSet)
router.register("sports-fields", SportsFieldViewSet)
router.register("bookings", BookingViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "service"
