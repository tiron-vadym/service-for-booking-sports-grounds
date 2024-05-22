from django.urls import path, include
from rest_framework import routers

from about.views import (
    FAQViewSet,
    FeedbackViewSet
)

router = routers.DefaultRouter()
router.register("faq", FAQViewSet)
router.register("feedbacks", FeedbackViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "about"
