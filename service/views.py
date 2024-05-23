from datetime import datetime, timedelta

import stripe
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from service.serializers import (
    SportGroundSerializer,
    SportGroundImageSerializer,
    SportGroundReservationSerializer,
    ReservationSerializer,
    ReservationListRetrieveSerializer,
    PaymentSerializer,
    SportGroundScheduleSerializer, ScheduleRetrieveSerializer
)
from service.models import SportGround, Reservation, Payment
from service.permissions import IsAdminOrReadOnly
from utilities.stripe import stripe_helper


class SportGroundViewSet(ModelViewSet):
    queryset = SportGround.objects.all()
    serializer_class = SportGroundSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "upload_image":
            return SportGroundImageSerializer
        if self.action == "reservation":
            return SportGroundReservationSerializer
        if self.action == "schedule":
            return SportGroundScheduleSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        activity = self.request.query_params.get("activity")
        location = self.request.query_params.get("location")
        date_str = self.request.query_params.get("date")
        time_str = self.request.query_params.get("time")

        if activity:
            queryset = queryset.filter(activity__iexact=activity)
        if location:
            queryset = queryset.filter(location__icontains=location)

        if date_str and time_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                time = datetime.strptime(time_str, "%H:%M").time()

                conflicting_reservations = Reservation.objects.filter(
                    day=date,
                    time__lte=(datetime.combine(
                        date,
                        time
                    ) + timedelta(hours=6)).time(),
                    place__in=queryset
                )
                for reservation in conflicting_reservations:
                    end_time = (
                            datetime.combine(
                                reservation.day,
                                reservation.time
                            ) +
                            timedelta(hours=reservation.duration_hours)
                    ).time()
                    if time < end_time:
                        queryset = queryset.exclude(id=reservation.place.id)
            except ValueError:
                return queryset.none()
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="activity",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter sports grounds by activity",
            ),
            OpenApiParameter(
                name="location",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter sports grounds by location",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter sports grounds by date",
            ),
            OpenApiParameter(
                name="time",
                type=OpenApiTypes.TIME,
                location=OpenApiParameter.QUERY,
                description="Filter sports grounds by time",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["GET"])
    def schedule(self, request, pk=None):
        sport_ground = self.get_object()
        reservations = sport_ground.reservations.all()
        return Response(
            {"schedule": ScheduleRetrieveSerializer(
                reservations,
                many=True
            ).data},
            status=status.HTTP_200_OK
        )

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        sport_ground = self.get_object()
        serializer = self.get_serializer(sport_ground, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="reservation",
        permission_classes=[IsAuthenticated]
    )
    def reservation(self, request, pk=None):
        sport_ground = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(place=sport_ground, personal_data=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.select_related(
        "place",
        "personal_data"
    ).all()
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


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related(
        "reservation"
    ).all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                reservation__personal_data=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(reservation__personal_data=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_id = serializer.data.get("id")
        reservation = Reservation.objects.get(id=reservation_id)
        stripe_helper(reservation)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=True, methods=["GET"], url_path="success")
    def success(self, request, pk=None):
        payment = Payment.objects.get(id=pk)
        session = stripe.checkout.Session.retrieve(payment.session_id)
        if session.payment_status == "paid":
            payment.status = "PAID"
            payment.save()
            return Response(
                {"message": "Payment success"}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Payment wasn't paid"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["GET"], url_path="cancel")
    def cancel(self, request, pk=None):
        return Response(
            {"message": "Payment canceled"},
            status=status.HTTP_200_OK
        )
