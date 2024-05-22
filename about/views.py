from rest_framework.viewsets import ModelViewSet

from about.models import FAQ, Feedback
from about.serializers import FAQSerializer, FeedbackSerializer
from service.permissions import IsAdminOrReadOnly


class FAQViewSet(ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = IsAdminOrReadOnly


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = IsAdminOrReadOnly
