from django.contrib import admin

from .models import User, Truck, Loadout, LoadoutBunch, CollectionCenter, Warehouse, Role, CratesManagementLog



admin.site.register(CratesManagementLog)
admin.site.register(User)
admin.site.register(Truck)
admin.site.register(Loadout)
admin.site.register(LoadoutBunch)
admin.site.register(CollectionCenter)
admin.site.register(Warehouse)
admin.site.register(Role)