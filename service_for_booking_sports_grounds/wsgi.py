"""
WSGI config for service_for_booking_sports_grounds project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "service_for_booking_sports_grounds.settings"
)

application = get_wsgi_application()
