from datetime import datetime, timedelta

import stripe
from django.db import transaction
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from service.serializers import (
    SportsComplexSerializer,
    SportsComplexRetrieveSerializer,
    SportsComplexImageSerializer,
    SportsFieldSerializer,
    SportsFieldBookingSerializer,
    BookingSerializer,
    PaymentSerializer
)
from service.models import SportsComplex, SportsField, Booking, Payment
from service.permissions import IsAdminOrReadOnly
from utilities.stripe import stripe_helper


class SportsComplexViewSet(ModelViewSet):
    queryset = SportsComplex.objects.all()
    serializer_class = SportsComplexSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SportsComplexRetrieveSerializer
        if self.action == "upload_image":
            return SportsComplexImageSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        activity = self.request.query_params.get("activity")
        location = self.request.query_params.get("location")
        date_str = self.request.query_params.get("date")
        time_str = self.request.query_params.get("time")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("fields__bookings")

        field_queryset = SportsField.objects.all()

        if activity:
            field_queryset = field_queryset.filter(activity__iexact=activity)
        if location:
            queryset = queryset.filter(location__iexact=location)

        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                conflicting_bookings_date = Booking.objects.filter(day=date)
                for booking in conflicting_bookings_date:
                    field_queryset = field_queryset.exclude(
                        id=booking.field.id
                    )
            except ValueError:
                return queryset.none()

        if time_str:
            try:
                time = datetime.strptime(time_str, "%H:%M").time()
                conflicting_bookings_time = Booking.objects.filter(
                    Q(time__lte=(datetime.combine(datetime.today(), time)
                                 + timedelta(hours=1)).time())
                    & Q(time__gte=(datetime.combine(datetime.today(), time)
                                   - timedelta(hours=1)).time())
                )

                for booking in conflicting_bookings_time:
                    field_queryset = field_queryset.exclude(
                        id=booking.field.id
                    )
            except ValueError:
                return queryset.none()

        queryset = queryset.filter(fields__in=field_queryset).distinct()
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="activity",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter sports complexes by activity",
            ),
            OpenApiParameter(
                name="location",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter sports complexes by location",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter sports complex by date",
            ),
            OpenApiParameter(
                name="time",
                type=OpenApiTypes.TIME,
                location=OpenApiParameter.QUERY,
                description="Filter sports complexes by time",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        sports_complex = self.get_object()
        serializer = self.get_serializer(sports_complex, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SportsFieldViewSet(ModelViewSet):
    queryset = SportsField.objects.select_related("complex").all()
    serializer_class = SportsFieldSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "booking":
            return SportsFieldBookingSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="booking",
        permission_classes=[IsAuthenticated]
    )
    def booking(self, request, pk=None):
        sports_field = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(field=sports_field, personal_data=request.user)
        return Response(
            serializer.to_representation(serializer.created_bookings),
            status=status.HTTP_200_OK
        )


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.select_related(
        "field",
        "personal_data"
    ).all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(personal_data=self.request.user)

    def perform_create(self, serializer):
        serializer.save(personal_data=self.request.user)


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related(
        "booking"
    ).all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                booking__personal_data=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(booking__personal_data=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]
        payment = stripe_helper(booking)

        serializer = self.get_serializer(payment[0])
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
