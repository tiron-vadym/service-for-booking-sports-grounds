from django.urls import path, include
from rest_framework import routers

from service.views import SportGroundViewSet, ReservationViewSet, FAQView

router = routers.DefaultRouter()
router.register("sports-grounds", SportGroundViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("about/", FAQView.as_view(), name="about"),
]

app_name = "service"
