from rest_framework import serializers
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import Loadout, CollectionCenter, LoadoutBunch, User, Warehouse, CratesManagementLog, Truck



class EmptyTruckEntryCheckSerializer(serializers.Serializer):
    truck_id = serializers.IntegerField(write_only=True)

    def validate(self, data):
        truck = data.get('truck_id')
        if truck <= 0:
            raise serializers.ValidationError({
                "truck_id": "Truck ID must be a positive number."})

        if not Truck.objects.filter(id=truck).exists():
            raise serializers.ValidationError({
                "truck_id": "Truck with this ID does not exist."})

        truck = Truck.objects.get(id=truck)
        if truck.status == "ACTIVE":
            raise serializers.ValidationError({
                "truck_id": "This Truck is not avaiable."})

        return data

    def create(self, validated_data):
        user = self.context.get("user")
        warehouse = Warehouse.objects.filter(security_gate_keeper = user).first()
        cc = CollectionCenter.objects.filter(floor_supervisor = user).first()
        place = "collection_center" if cc else "warehouse"
        source_location = cc if cc else warehouse
        truck = Truck.objects.get(id=validated_data['truck_id'])
        loadout_bunch = LoadoutBunch.objects.create(**{place:source_location},truck=truck)
        truck.status = "ACTIVE"
        truck.save()
        return loadout_bunch


class LoadCrateItemSerializer(serializers.Serializer):
    center = serializers.IntegerField()
    crates = serializers.IntegerField()

    def validate(self, attrs):
        warehouse = Warehouse.objects.filter(operation_officer=self.context.get('user'))
        collectioncenter = CollectionCenter.objects.filter(floor_supervisor=self.context.get('user'))
        location = CollectionCenter if warehouse else Warehouse
        print()
        try:
            cc = location.objects.get(id=attrs["center"])
        except location.DoesNotExist:
            raise serializers.ValidationError({
                "center": f"{location} with ID {attrs['center']} does not exist."
            })
        available_capacity = cc.capacity - cc.total_crates
        if available_capacity < attrs["crates"]:
            raise serializers.ValidationError({
                "crates": f"Collection center '{cc.located_at}' has insufficient capacity. "
                          f"Available capacity: {available_capacity}, Requested: {attrs['crates']}"
            })
        attrs['location'] = location
        return attrs


class LoadCratesSerializer(serializers.Serializer):
    id = serializers.IntegerField(write_only=True)
    multiple_data = LoadCrateItemSerializer(many=True)

    def validate(self, attrs):
        multiple_data = attrs.get('multiple_data')
        id = attrs.get('id')
        total_crates_in_request = sum(item['crates'] for item in multiple_data)
        warehouse = Warehouse.objects.filter(operation_officer=self.context.get('user')).first()
        collectioncenter = CollectionCenter.objects.filter(floor_supervisor=self.context.get('user')).first()
        center = warehouse if warehouse else collectioncenter
        crates = center.filled_crates if collectioncenter else center.empty_crates

        if crates < total_crates_in_request:
            raise serializers.ValidationError({
                "crates": f"{center.located_at} has insufficient crates. "
                         f"Available crates: {crates}, "
                         f"Total requested: {total_crates_in_request}"})

        loadout_bunch = get_object_or_404(LoadoutBunch, id=id)

        if total_crates_in_request > loadout_bunch.truck.capacity:
            raise serializers.ValidationError({
                "crates": f"Truck capacity is of {loadout_bunch.truck.capacity} crates."})
        attrs['location'] = CollectionCenter if warehouse else Warehouse
        return attrs

    def create(self, validated_data):
        warehouse = Warehouse.objects.filter(operation_officer=self.context.get('user')).first()
        collectioncenter = CollectionCenter.objects.filter(floor_supervisor=self.context.get('user')).first()
        if collectioncenter:
            source_location = collectioncenter
            destination_location_type = "warehouse"

        elif warehouse:
            source_location = warehouse
            destination_location_type = "collection_center"

        loadout_bunch = get_object_or_404(LoadoutBunch, id=validated_data['id'])
        total_crates = 0
        loadouts = []
        for item in validated_data['multiple_data']:
            total_crates += item['crates']
            collection_center_instance = validated_data['location'].objects.get(id=item['center'])
            loadouts.append(
                Loadout(
                loadout_bunch=loadout_bunch,
                **{destination_location_type:collection_center_instance},
                crates=item['crates']))

        loadout_bunch.crates = total_crates
        loadout_bunch.load_at = timezone.now()
        loadout_bunch.loadoutBunch_status = "LOADED"
        loadout_bunch.save()
        result = Loadout.objects.bulk_create(loadouts)
        if warehouse:
            source_location.empty_crates -= total_crates
            source_location.total_crates -= total_crates
            loadout_bunch.truck.empty_crates = total_crates

        elif collectioncenter:
            source_location.filled_crates -= total_crates
            source_location.total_crates -= total_crates
            loadout_bunch.truck.filled_crates = total_crates

        source_location.save()
        loadout_bunch.truck.total_crates = total_crates
        loadout_bunch.truck.save()
        return result


class UnloadCratesEntrySerializer(serializers.Serializer):
    damage_crates = serializers.IntegerField(required=True)
    missing_crates = serializers.IntegerField(required=True)
    proper_crates = serializers.IntegerField(required=True)

    class Meta:
        fields = ("damage_crates", "missing_crates", "proper_crates")

    def validate(self, attrs):
        id = self.context.get('pk')
        total_crates = attrs.get('damage_crates') + attrs.get('missing_crates') + attrs.get('proper_crates')
        loadout = Loadout.objects.get(id=id)
        if loadout.crates != total_crates:
            raise serializers.ValidationError(f"As per you there are {total_crates} crates. But truck has {loadout.crates}")
        return attrs

    def update(self, instance, validated_data):
        id = self.context.get('pk')
        loadout = Loadout.objects.get(id=id)
        total_crates = validated_data.get('damage_crates') + validated_data.get('missing_crates') + validated_data.get('proper_crates')
        truck = loadout.loadout_bunch.truck
        log = CratesManagementLog.objects.get(loadout=loadout)
        log.missing_crates = validated_data['missing_crates']
        log.damaged_crates = validated_data['damage_crates']

        location = loadout.collection_center if loadout.collection_center else loadout.warehouse
        location.damage_crates += validated_data['damage_crates']
        location.missing_crates += validated_data['missing_crates']
        location.total_crates += validated_data['damage_crates'] + validated_data['proper_crates']

        if loadout.collection_center:
            location.empty_crates += validated_data['proper_crates']
            truck.empty_crates -= total_crates
            log.empty_crates -= validated_data['damage_crates']
            log.empty_crates -= validated_data['missing_crates']
            loadout.truck_status = "EXITED"
            next_loadout = Loadout.objects.filter(loadout_bunch=loadout.loadout_bunch, id__gt=loadout.id).order_by('id').first()
            if next_loadout:
                next_loadout.truck_status = "COMING"
                next_loadout.save()

            elif not next_loadout:
                loadout.loadout_bunch.loadoutBunch_status = "COMPLETED"
                loadout.loadout_bunch.save()

        elif loadout.warehouse:
            location.filled_crates += validated_data['proper_crates']
            truck.filled_crates -= total_crates
            log.filled_crates -= validated_data['damage_crates']
            log.filled_crates -= validated_data['missing_crates']
            loadout.truck_status = "UNLOADED"
            next_loadout = Loadout.objects.filter(loadout_bunch=loadout.loadout_bunch, id__gt=loadout.id).order_by('id').first()

            if not next_loadout:
                loadout.truck_status = "EXITED"
                loadout.loadout_bunch.loadoutBunch_status = "COMPLETED"
                loadout.loadout_bunch.save()
                loadout.save()

        location.save()
        log.total_crates -= validated_data['missing_crates']
        log.save()
        loadout.unload_at = timezone.now()
        loadout.save()
        truck.total_crates -= total_crates
        truck.save()
        if truck.total_crates == 0:
            truck.status = "INACTIVE"
            truck.save()

        return validated_data