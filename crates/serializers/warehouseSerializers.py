from rest_framework import serializers

from ..models import Loadout, CollectionCenter, LoadoutBunch, Warehouse



class LoadEmptyCratesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loadout
        fields = ('collection_center', 'crates', 'truck_id')

    def validate(self, attrs):
        collection_center = attrs.get('collection_center')
        crates = attrs.get('crates')
        cc = CollectionCenter.objects.get(id=collection_center)
 
        if  cc.capacity-cc.total_crates < crates:
            raise serializers.ValidationError(f"{cc.located_at} Collection center does not have enough capacity.")
        warehouse = Warehouse.objects.get(operation_officer=self.context.get('user'))

        total_crates_in_request = sum(crates)
        if warehouse.total_crates < total_crates_in_request:
            raise serializers.ValidationError("Warehouse does not have enough crates for this operation.")

        return attrs

    def create(self, validated_data):
        user = self.context.get('user')
        warehouse = Warehouse.objects.get(operation_officer=user)
        loadoutBunch = LoadoutBunch.objects.create(
            warehouse=warehouse,
            truck_id=validated_data.get('truck_id'))
        
        loadout = [Loadout(**i, loadout_bunch_id=loadoutBunch) for i in validated_data]
        Loadout.objects.bulk_create(loadout)

        return loadoutBunch
