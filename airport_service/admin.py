from django.contrib import admin

from airport_service.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Ticket,
    Order,
    Flight
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Flight)
