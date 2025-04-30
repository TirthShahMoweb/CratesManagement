from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.baseModel import BaseModel
from CratesManagement import settings


class UserTypeChoices(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    DRIVER = 'driver', 'Driver'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True, max_length=255)
    mobile_number = models.CharField(max_length=15)
    type = models.CharField(max_length=50, choices=UserTypeChoices)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)


class Role(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


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
    operation_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


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
    total_crates = models.IntegerField(null=True, blank=True)
    filled_crates = models.IntegerField(null=True, blank=True)
    empty_crates = models.IntegerField(null=True, blank=True)


class LoadoutStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    REJECTED = 'REJECTED', 'Rejected'
    APPROVED = 'APPROVED', 'Approved'


class LoadoutBunch(BaseModel):
    collection_center = models.ForeignKey(CollectionCenter, on_delete=models.CASCADE,null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,null=True, blank=True)
    truck_id = models.ForeignKey(Truck, on_delete=models.CASCADE)
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LoadoutStatus, default='PENDING')
    dispatch_at = models.DateTimeField(null=True, blank=True)


class Loadout(BaseModel):
    collection_center = models.ForeignKey(CollectionCenter, on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    loadout_bunch_id = models.ForeignKey('LoadoutBunch', on_delete=models.CASCADE)
    crates = models.IntegerField()
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=LoadoutStatus, default='PENDING')
    unload_at = models.DateTimeField(null=True, blank=True)
    sg_exit_at = models.DateTimeField(null=True, blank=True)