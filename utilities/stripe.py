from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
import stripe

from service.models import Booking, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def calculate_total_amount(
        booking: Booking
) -> int:
    price_cents = booking.field.price * 100
    looking_price = int(price_cents)

    return stripe.Price.create(
        product="prod_Pz5uWC2BXMLDzx",
        unit_amount=looking_price,
        currency="usd",
    )


def session(price, payment):
    request = HttpRequest()
    request.META["SERVER_NAME"] = settings.SERVER_NAME
    request.META["SERVER_PORT"] = settings.SERVER_PORT
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": price,
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            location=reverse("service:payment-success",
                             kwargs={"pk": payment.id})
        ),
        cancel_url=request.build_absolute_uri(
            location=reverse("service:payment-cancel",
                             kwargs={"pk": payment.id})
        ),
    )
    return checkout_session


def stripe_helper(booking: Booking):
    price = calculate_total_amount(booking)
    payment = Payment.objects.create(
        booking=booking,
        money_to_pay=price["unit_amount"] / 100,
    )

    checkout_session = session(price, payment)
    payment.session_url = checkout_session.url
    payment.session_id = checkout_session.id
    payment.save()
    return payment, redirect(checkout_session.url, code=303)
