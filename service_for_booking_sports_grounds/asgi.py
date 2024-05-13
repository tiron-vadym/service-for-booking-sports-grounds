"""
ASGI config for service_for_booking_sports_grounds project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "service_for_booking_sports_grounds.settings"
)

application = get_asgi_application()
