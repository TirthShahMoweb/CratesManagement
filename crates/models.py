from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.baseModel import BaseModel
from CratesManagement import settings


class UserTypeChoices(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    DRIVER = 'driver', 'Driver'
    ADMIN = 'admin', 'Admin'


class Role(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True, max_length=255)
    mobile_number = models.CharField(max_length=15)
    type = models.CharField(max_length=50, choices=UserTypeChoices)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)


class Warehouse(BaseModel):
    located_at = models.CharField(max_length=255)
    total_crates = models.IntegerField(null=True, blank=True)
    filled_crates = models.IntegerField(null=True, blank=True)
    empty_crates = models.IntegerField(null=True, blank=True)
    damage_crates = models.IntegerField(null=True, blank=True)
    missing_crates = models.IntegerField(null=True, blank=True)
    container_crates = models.IntegerField(null=True, blank=True)
    ready_to_sell_crates = models.IntegerField(null=True, blank=True)
    capacity = models.IntegerField()
    operation_officer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    warehouse_manager = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_warehouses', null=True, blank=True)
    security_gate_keeper = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='security_gate_keeper_warehouse', null=True, blank=True)


class CollectionCenter(BaseModel):
    located_at = models.CharField(max_length=255)
    total_crates = models.IntegerField(null=True, blank=True)
    filled_crates = models.IntegerField(null=True, blank=True)
    empty_crates = models.IntegerField(null=True, blank=True)
    damage_crates = models.IntegerField(null=True, blank=True)
    missing_crates = models.IntegerField(null=True, blank=True)
    capacity = models.IntegerField()
    floor_supervisor = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supervised_centers', null=True, blank=True)
    zonal_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_zones', null=True, blank=True)


class VehicleStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    UNDER_MAINTENANCE = 'UNDER_MAINTENANCE', 'Under Maintenance'


class Truck(BaseModel):
    number_plate = models.CharField(max_length=20)
    status = models.CharField(max_length=50, choices=VehicleStatus)
    capacity = models.IntegerField()
    total_crates = models.IntegerField(null=True, blank=True, default=0)
    filled_crates = models.IntegerField(null=True, blank=True, default=0)
    empty_crates = models.IntegerField(null=True, blank=True, default=0)


class LoadoutStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    REJECTED = 'REJECTED', 'Rejected'
    APPROVED = 'APPROVED', 'Approved'


class TruckStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    GOING = 'GOING', 'Going'
    ENTRY_CHECKED = 'ENTRY_CHECKED', 'Entry Checked'
    UNLOADED = 'UNLOADED', 'Unloaded'
    EXITED = 'EXITED', 'Exited'


class LoadoutBunchStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    LOADED = 'LOADED', 'Loaded'
    APPROVED = 'APPROVED', 'Approved'
    DISPATCHED = 'DISPATCHED', 'Dispatched'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'


class LoadoutBunch(BaseModel):
    collection_center = models.ForeignKey(CollectionCenter, on_delete=models.CASCADE,null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,null=True, blank=True)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    load_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    crates = models.IntegerField(null=True, blank=True, default=0)
    status = models.CharField(max_length=20, choices=LoadoutStatus, default='PENDING')
    dispatch_at = models.DateTimeField(null=True, blank=True)
    sg_exit_at = models.DateTimeField(null=True, blank=True)
    loadoutBunch_status = models.CharField(max_length=20, choices=LoadoutBunchStatus, default='PENDING')


class Loadout(BaseModel):
    collection_center = models.ForeignKey(CollectionCenter, on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    loadout_bunch = models.ForeignKey(LoadoutBunch, on_delete=models.CASCADE, related_name='loadout_loadoutbunch')
    crates = models.IntegerField(null=True, blank=True, default=0)
    entryCheck_at = models.DateTimeField(null=True, blank=True)
    entrycheck_status = models.CharField(max_length=50, choices=LoadoutStatus, default='PENDING')
    truck_status = models.CharField(max_length=50, choices=TruckStatus, default='PENDING')
    unload_at = models.DateTimeField(null=True, blank=True)
    sg_exit_at = models.DateTimeField(null=True, blank=True)


class CratesManagementLog(BaseModel):
    from_location_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=models.Q(app_label='crates', model__in=['warehouse', 'collectioncenter']), related_name='from_location_logs')
    from_location_object_id = models.PositiveIntegerField()
    from_location = GenericForeignKey('from_location_content_type', 'from_location_object_id')
    to_location_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=models.Q(app_label='crates', model__in=['warehouse', 'collectioncenter']), related_name='to_location_logs')
    to_location_object_id = models.PositiveIntegerField()
    to_location = GenericForeignKey('to_location_content_type', 'to_location_object_id')
    loadout = models.ForeignKey(Loadout, on_delete=models.CASCADE, related_name='cratesmanagementlog_loadout')
    total_crates = models.IntegerField(default=0, null=True, blank=True)
    filled_crates = models.IntegerField(default=0, null=True, blank=True)
    empty_crates = models.IntegerField(default=0, null=True, blank=True)
    missing_crates = models.IntegerField(default=0, null=True, blank=True)
    damaged_crates = models.IntegerField(default=0, null=True, blank=True)


class StockInEmptyCrates(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    vendor_description = models.TextField(null=True, blank=True)
    crates = models.IntegerField(default=0)


# class SRManagementLog(BaseModel):
#     warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name="sr_warehouse")
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_warehouses', null=True, blank=True)
#     total_crates = models.IntegerField(default=0, null=True, blank=True)
#     filled_crates = models.IntegerField(default=0, null=True, blank=True)
#     empty_crates = models.IntegerField(default=0, null=True, blank=True)
#     missing_crates = models.IntegerField(default=0, null=True, blank=True)
#     damaged_crates = models.IntegerField(default=0, null=True, blank=True)