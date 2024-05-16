from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from service.serializers import (
    SportGroundSerializer,
    SportGroundImageSerializer,
    ReservationSerializer,
    ReservationListRetrieveSerializer
)
from service.models import SportGround, Reservation
from service.permissions import IsAdminOrReadOnly


class SportGroundViewSet(ModelViewSet):
    queryset = SportGround.objects.all()
    serializer_class = SportGroundSerializer
    # permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return SportGroundImageSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        price = self.request.query_params.get("price")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if price:
            queryset = queryset.filter(price=price)

        return queryset

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        sport_ground = self.get_object()
        serializer = self.get_serializer(sport_ground, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.select_related("place").all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(personal_data=self.request.user)

    def perform_create(self, serializer):
        serializer.save(personal_data=self.request.user)

    def get_serializer_class(self):
        serializer_classes = {
            "list": ReservationListRetrieveSerializer,
            "retrieve": ReservationListRetrieveSerializer,
        }
        return serializer_classes.get(self.action, ReservationSerializer)
