from django.contrib import admin
from .models import Location, CollectionPlan, CollectionRequest

admin.site.register(CollectionRequest)
admin.site.register(Location)
admin.site.register(CollectionPlan)
