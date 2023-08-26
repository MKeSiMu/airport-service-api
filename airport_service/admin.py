from django.contrib import admin

from airport_service.models import AirplaneType, Airplane, Crew, Airport, Route

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(Route)
