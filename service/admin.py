from django.contrib import admin

from service.models import SportsComplex, SportsField, Booking


admin.site.register(SportsComplex)
admin.site.register(SportsField)
admin.site.register(Booking)
