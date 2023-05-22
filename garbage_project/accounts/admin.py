from django.contrib import admin
from .models import GarbageCollector, CustomerProfile, CustomUser

admin.site.register(GarbageCollector)
admin.site.register(CustomerProfile)
admin.site.register(CustomUser)