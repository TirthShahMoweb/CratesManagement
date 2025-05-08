from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, F, Q

from ..serializers.warehouseSerializers import LoadCratesSerializer, BuyingEmptyCratesSerializer, EmptyTruckEntryCheckSerializer, UnloadCratesEntrySerializer
from ..models import CollectionCenter, Warehouse, LoadoutBunch, Loadout, User, CratesManagementLog, Truck



class CanVerifyTruckPermission(BasePermission):

    def __init__(self, id):
        self.id = id

    def has_permission(self, request, view):
        try:
            loadout_bunch = LoadoutBunch.objects.get(id=self.id)
        except:
            return Response({"status": "error", "message": "LoadoutBunch not found"}, status=status.HTTP_404_NOT_FOUND)

        if loadout_bunch.warehouse:
            if loadout_bunch.warehouse.warehouse_manager == request.user:
                return True
            return False

        if loadout_bunch.collection_center:
            if loadout_bunch.collection_center.zonal_manager == request.user:
                return True
            return False

class CanEntrycheckPermission(BasePermission):

    def __init__(self, id):
        self.id = id

    def has_permission(self, request, view):
        try:
            loadout = Loadout.objects.get(id=self.id)
        except:
            return Response({"status": "error", "message": "Loadout not found"}, status=status.HTTP_404_NOT_FOUND)
        if loadout.warehouse:
            if loadout.warehouse.security_gate_keeper == request.user:
                return True
            return False

        if loadout.collection_center:
            if loadout.collection_center.floor_supervisor == request.user:
                return True
            return False

class CanDispatchTruckPermission(BasePermission):

    def __init__(self, id):
        self.id = id

    def has_permission(self, request, view):
        try:
            loadout_bunch = LoadoutBunch.objects.get(id=self.id)
        except:
            return Response({"status": "error", "message": "LoadoutBunch not found"}, status=status.HTTP_404_NOT_FOUND)

        if loadout_bunch.warehouse:
            if loadout_bunch.warehouse.operation_officer == request.user:
                return True
            return False

        if loadout_bunch.collection_center:
            print(request.user)
            print(loadout_bunch.collection_center.floor_supervisor)
            if loadout_bunch.collection_center.floor_supervisor == request.user:
                return True
            return False

class CanUnloadTruckPermission(BasePermission):

    def __init__(self, id):
        self.id = id

    def has_permission(self, request, view):
        try:
            loadout = Loadout.objects.get(id=self.id)
        except:
            return Response({"status": "error", "message": "Loadout not found"}, status=status.HTTP_404_NOT_FOUND)
        if loadout.warehouse:
            if loadout.warehouse.operation_officer == request.user:
                return True
            return False

        if loadout.collection_center:
            if loadout.collection_center.floor_supervisor == request.user:
                return True
            return False

class CanExitcheckPermission(BasePermission):

    def __init__(self, id):
        self.id = id

    def has_permission(self, request, view):
        try:
            loadout = Loadout.objects.get(id=self.id)
        except:
            return Response({"status": "error", "message": "Loadout Bunch not found"}, status=status.HTTP_404_NOT_FOUND)
        warehouse = loadout.warehouse or loadout.loadout_bunch.warehouse
        cc = loadout.collection_center or loadout.loadout_bunch.collection_center
        if warehouse:
            if warehouse.security_gate_keeper == request.user:
                return True
            return False
        elif cc:
            if cc.floor_supervisor == request.user:
                return True
            return False

class CanLoadTruckPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        warehouse = Warehouse.objects.filter(Q(operation_officer=user) | Q(warehouse_manager=user)).first()
        cc = CollectionCenter.objects.filter(Q(floor_supervisor=user) | Q(zonal_manager=user)).first()
        if warehouse or cc:
            return True
        return False

class CanBuyingEmptyCratesPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        print(user)
        warehouse = Warehouse.objects.filter(operation_officer = user).first()
        if warehouse:
            return True
        return False

class CanEmptyTruckEntryCheckPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        warehouse = Warehouse.objects.filter(security_gate_keeper = user).first()
        cc = CollectionCenter.objects.filter(floor_supervisor = user).first()
        if warehouse or cc:
            return True
        return False

class EmptyTruckEntryCheckView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanEmptyTruckEntryCheckPermission]
    serializer_class = EmptyTruckEntryCheckSerializer


    def get_object(self):
        return get_object_or_404(User, username=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"status":"success","message": "Truck got successfully entired."}, status=status.HTTP_200_OK)


class LoadCratesView(CreateAPIView):
    serializer_class = LoadCratesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanLoadTruckPermission]

    def get_object(self):
        return get_object_or_404(User, username=self.request.user)


    def create(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        loadouts = self.perform_create(serializer)
        validated_data = serializer.validated_data
        data=[]

        for i in validated_data['multiple_data']:
            cc = validated_data['location'].objects.get(id=i['center'])
            cc_data = {"location":cc.located_at,"crates":i['crates']}
            data.append(cc_data)
        loadout_bunch = LoadoutBunch.objects.get(id=validated_data['id'])
        data.append({"Truck":loadout_bunch.truck.number_plate})
        return Response({"status":"success","message": "Crates loaded successfully","data":data}, status=status.HTTP_201_CREATED)


class VerifyTruckView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), CanVerifyTruckPermission(self.kwargs.get('pk'))]

    def get_object(self):
        id = self.kwargs.get('pk')
        return get_object_or_404(LoadoutBunch, id=id)

    def update(self, request, *args, **kwargs):
        loadout_bunch = self.get_object()
        if not loadout_bunch:
            return Response(
                {"status": "error","message": "No loadout bunch found for this"},
                status=status.HTTP_404_NOT_FOUND)

        loadout_bunch.status = 'APPROVED'
        loadout_bunch.verified_at = timezone.now()
        loadout_bunch.loadoutBunch_status = "APPROVED"
        loadout_bunch.save()

        from_location_obj = loadout_bunch.warehouse or loadout_bunch.collection_center
        from_location_ct = ContentType.objects.get_for_model(from_location_obj.__class__)
        from_location_id = from_location_obj.id
        loadouts = loadout_bunch.loadout_loadoutbunch.select_related('collection_center', 'warehouse').order_by('id')

        for loadout in loadouts:
            to_location_obj = loadout.collection_center or loadout.warehouse
            to_location_ct = ContentType.objects.get_for_model(to_location_obj.__class__)
            to_location_id = to_location_obj.id

            # Create the log entry
            log = CratesManagementLog.objects.create(
                from_location_content_type=from_location_ct,
                from_location_object_id=from_location_id,
                to_location_content_type=to_location_ct,
                to_location_object_id=to_location_id,
                loadout=loadout,
                total_crates=loadout.crates,
                empty_crates=loadout.crates if loadout.collection_center else 0,
                filled_crates=loadout.crates if loadout.warehouse else 0
            )

            from_location_ct = to_location_ct
            from_location_id = to_location_id
            from_location_obj = to_location_obj

        return Response(
            {"status": "success", "message": "Successfully approved"},
            status=status.HTTP_200_OK
        )


class DispatchTruckView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), CanDispatchTruckPermission(self.kwargs.get('pk'))]


    def get_object(self):
        id = self.kwargs.get('pk')
        user = self.request.user
        try:
            loadout_bunch = LoadoutBunch.objects.get(id=id)
            return loadout_bunch
        except LoadoutBunch.DoesNotExist:
            return None

    def update(self, request, *args, **kwargs):
        loadout_bunch = self.get_object()
        if not loadout_bunch:
            return Response(
                {"status": "error","message": "No loadout bunch found for this"},
                status=status.HTTP_404_NOT_FOUND
            )

        if loadout_bunch.status != 'APPROVED' or not loadout_bunch.verified_at:
            return Response(
                {"status": "error","message": "wait for approval by warehouse Manager."},
                status=status.HTTP_404_NOT_FOUND
            )

        loadout_bunch.dispatch_at = timezone.now()
        if loadout_bunch.collection_center:
            loadout_bunch.loadoutBunch_status = "IN_PROGRESS"
            loadout = loadout_bunch.loadout_loadoutbunch.first()
            loadout.truck_status = "GOING"
            loadout.save()
        elif loadout_bunch.warehouse:
            loadout_bunch.loadoutBunch_status = "DISPATCHED"
        loadout_bunch.save()


        return Response({"status": "success", "message": "Truck dispatched successfully"}, status=status.HTTP_200_OK)


class ExitcheckView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), CanExitcheckPermission(self.kwargs.get('pk'))]

    def get_object(self):
        id = self.kwargs.get('pk')
        return get_object_or_404(Loadout, id=id)

    def update(self, request, *args, **kwargs):
        loadout = self.get_object()
        if not loadout:
            return Response({"status": "error","message": "No loadout found for this"},status=status.HTTP_404_NOT_FOUND)

        if loadout.loadout_bunch.warehouse:
            if not loadout.loadout_bunch.sg_exit_at:
                if not loadout.loadout_bunch.dispatch_at:
                    return Response({"status": "error","message": "Wait till the Truck got Dispatch."},status=status.HTTP_404_NOT_FOUND)
                else:
                    loadout_bunch=loadout.loadout_bunch
                    loadout_bunch.sg_exit_at= timezone.now()
                    loadout_bunch.loadoutBunch_status = "IN_PROGRESS"
                    loadout_bunch.save()
                    loadout.truck_status = "GOING"
                    loadout.save()
                    return Response({"status": "success","message": "Truck got successfully exited.",},status=status.HTTP_200_OK)

        elif loadout.warehouse:
            if not loadout.unload_at:
                return Response({"status": "error", "message": "Wait until the truck is unloaded."}, status=status.HTTP_400_BAD_REQUEST)
            loadout.sg_exit_at = timezone.now()
            loadout.truck_status = "EXITED"
            loadout.save()
            next_loadout = Loadout.objects.filter(loadout_bunch=loadout.loadout_bunch, id__gt=loadout.id).order_by('id').first()
            if next_loadout:
                next_loadout.truck_status = "GOING"
                next_loadout.save()

            return Response({"status": "success", "message": "Truck successfully exited from warehouse."}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Invalid loadout configuration."}, status=status.HTTP_400_BAD_REQUEST)


class EntrycheckView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), CanEntrycheckPermission(self.kwargs.get('pk'))]

    def get_object(self):
        id = self.kwargs.get('pk')
        return get_object_or_404(Loadout, id=id)

    def update(self, request, *args, **kwargs):
        loadout = self.get_object()

        if loadout.warehouse:
            previous_loadout = Loadout.objects.filter(loadout_bunch=loadout.loadout_bunch, id__lt=loadout.id).order_by('-id').first()
            if previous_loadout and (not previous_loadout.sg_exit_at or previous_loadout.truck_status != "EXITED"):
                return Response({"status": "error", "message": f"Let truck get exited from {previous_loadout.warehouse.located_at}"}, status=status.HTTP_400_BAD_REQUEST)

        if loadout.collection_center:
            previous_loadout = Loadout.objects.filter(loadout_bunch=loadout.loadout_bunch, id__lt=loadout.id).order_by('-id').first()
            if previous_loadout and (not previous_loadout.unload_at or previous_loadout.truck_status != "EXITED"):
                return Response({"status": "error", "message": f"Let truck get exited from {previous_loadout.collection_center.located_at}"}, status=status.HTTP_400_BAD_REQUEST)

        if loadout.collection_center and loadout.loadout_bunch.warehouse:
            if not loadout.loadout_bunch.sg_exit_at:
                return Response({"status": "error", "message": "Wait till the truck exits from warehouse."}, status=status.HTTP_400_BAD_REQUEST)

        if not loadout.loadout_bunch.dispatch_at:
            return Response({"status": "error", "message": "Wait till the truck gets dispatched."}, status=status.HTTP_400_BAD_REQUEST)

        loadout.entryCheck_at = timezone.now()
        loadout.entrycheck_status = 'APPROVED'
        loadout.truck_status = "ENTRY_CHECKED"
        loadout.save()

        return Response({"status": "success", "message": "Entry Check done successfully"}, status=status.HTTP_200_OK)


class UnloadTruckView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), CanUnloadTruckPermission(self.kwargs.get('pk'))]
    serializer_class = UnloadCratesEntrySerializer

    def get_object(self):
        id = self.kwargs.get('pk')
        return get_object_or_404(Loadout, id=id)

    def update(self, request, *args, **kwargs):
        loadout = self.get_object()
        if not loadout:
            return Response({"status": "error","message": "No loadout found for this"},status=status.HTTP_400_BAD_REQUEST)

        if not loadout.entryCheck_at or loadout.entrycheck_status != 'APPROVED':
            return Response(
                {"status": "error", "message": "Wait until the truck completes entry check."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(loadout, data=request.data, context={'pk': self.kwargs.get('pk')})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"status": "success", "message": "Truck unloaded successfully."},
            status=status.HTTP_200_OK
        )


class CratesTracking(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanLoadTruckPermission]

    def get_queryset(self):
        user = self.request.user
        warehouse = Warehouse.objects.filter(Q(operation_officer=user) | Q(warehouse_manager=user)).first()
        cc = CollectionCenter.objects.filter(Q(floor_supervisor=user) | Q(zonal_manager=user)).first()

        if warehouse:
            # print(LoadoutBunch.objects.filter(~Q(loadoutBunch_status="COMPLETED"), warehouse=warehouse))
            return LoadoutBunch.objects.filter(~Q(loadoutBunch_status="COMPLETED"), warehouse=warehouse)

        elif cc:
            # print(LoadoutBunch.objects.filter(~Q(loadoutBunch_status="COMPLETED"), collection_center=cc))
            return LoadoutBunch.objects.filter(~Q(loadoutBunch_status="COMPLETED"), collection_center=cc)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        user = request.user
        warehouse = Warehouse.objects.filter(operation_officer=user).first()
        cc = CollectionCenter.objects.filter(floor_supervisor=user).first()
        loadouts = None
        if warehouse:
            loadouts = Loadout.objects.filter(Q(truck_status="ENTRY_CHECKED") | Q(truck_status="UNLOADED"),warehouse=warehouse).first()
            person = warehouse.security_gate_keeper
            crate_type = "filled_crates"
        elif cc:
            loadouts = Loadout.objects.filter(Q(truck_status="ENTRY_CHECKED") | Q(truck_status="UNLOADED"),collection_center=cc).first()
            person = cc.floor_supervisor
            crate_type = "empty_crates"

        if loadouts:
            action = "Unload" if loadouts.truck_status=="ENTRY_CHECKED" else "Waiting for Exit Check"
            single_data = {
                        "id": loadouts.id,
                        "vehicle_number_plate": loadouts.loadout_bunch.truck.number_plate,
                        "crates": loadouts.crates,
                        "crates_type": crate_type,
                        "status" : f"{action}",
                        "date_time": f"{loadouts.entryCheck_at}",
                        "action_by" : f"{person.first_name} {person.last_name}"
                        }
            data.append(single_data)

        wm = Warehouse.objects.filter(warehouse_manager=user).first()
        zm = cc = CollectionCenter.objects.filter(zonal_manager=user).first()
        person = wm.operation_officer if wm else zm.floor_supervisor
        if wm or zm:
            for loadout_bunch in queryset:
                crate_type = "filled_crates" if loadout_bunch.collection_center else "empty_crates"
                if loadout_bunch.loadoutBunch_status == "LOADED":
                    single_data = {
                    "id": loadout_bunch.id,
                    "vehicle_number_plate": loadout_bunch.truck.number_plate,
                    "crates": loadout_bunch.crates,
                    "crates_type": crate_type,
                    "status": "waiting_for_approval",
                    "date_time": f"{loadout_bunch.load_at}",
                    "action_by" : f"{person.first_name} {person.last_name}"
                    }
                data.append(single_data)
            return Response({"status": "success","message": "Successfully fetched the data.", "data":data},status=status.HTTP_200_OK)

        elif queryset:
            for loadout_bunch in queryset:
                loadout = loadout_bunch.loadout_loadoutbunch.filter(~Q(truck_status="EXITED")).order_by("id").first()
                crate_type = "filled_crates" if loadout_bunch.collection_center else "empty_crates"
                truck_tracking = loadout.truck_status.lower() if loadout_bunch.loadoutBunch_status=="IN_PROGRESS" else loadout_bunch.loadoutBunch_status

                if truck_tracking == "PENDING":
                    truck_tracking = "load_empty_crates" if loadout_bunch.warehouse else "load_filled_crates"
                    last_action_at = loadout_bunch.created_at
                    last_action_by = loadout_bunch.warehouse.security_gate_keeper if loadout_bunch.warehouse else loadout_bunch.collection_center.floor_supervisor

                elif truck_tracking == "LOADED":
                    truck_tracking = "waiting_for_approval"
                    last_action_at = loadout_bunch.load_at
                    last_action_by = loadout_bunch.warehouse.operation_officer if loadout_bunch.warehouse else loadout_bunch.collection_center.floor_supervisor

                elif truck_tracking == "APPROVED":
                    truck_tracking = "dispatch"
                    last_action_at = loadout_bunch.verified_at
                    last_action_by = loadout_bunch.warehouse.warehouse_manager if loadout_bunch.warehouse else loadout_bunch.collection_center.zonal_manager

                elif truck_tracking == "DISPATCHED":
                    truck_tracking = "waiting_for_exit_check" if loadout.warehouse else "going_to"
                    last_action_at = loadout_bunch.dispatch_at
                    last_action_by = loadout_bunch.warehouse.operation_officer if loadout_bunch.warehouse else loadout_bunch.collection_center.floor_supervisor

                single_data = {
                    "id": loadout_bunch.id,
                    "vehicle_number_plate": loadout_bunch.truck.number_plate,
                    "crates": loadout_bunch.crates,
                    "crates_type": crate_type,
                    "status": f"{truck_tracking}"
                    }

                if loadout_bunch.loadoutBunch_status == "IN_PROGRESS":
                    single_data["location"] = loadout.collection_center.located_at if loadout.collection_center else loadout.warehouse.located_at
                    if loadout.truck_status == "GOING":
                        first_loadout = loadout_bunch.loadout_loadoutbunch.all().order_by("id").first()
                        load_coming = Loadout.objects.filter(truck_status="GOING").order_by("id").first()
                        load_exited = Loadout.objects.filter(truck_status="EXITED").order_by("id").last()
                        if first_loadout == load_coming:
                            last_action_at = loadout_bunch.sg_exit_at if loadout_bunch.warehouse else loadout_bunch.dispatch_at
                            last_action_by = loadout_bunch.warehouse.security_gate_keeper if loadout_bunch.warehouse else loadout_bunch.collection_center.floor_supervisor
                        else:
                            last_action_at = load_exited.sg_exit_at if load_exited.warehouse else load_exited.unload_at
                            last_action_by = load_exited.warehouse.security_gate_keeper if load_exited.warehouse else load_exited.collection_center.floor_supervisor

                    elif loadout.truck_status == "ENTRY_CHECKED":
                        last_action_at = loadout.entryCheck_at
                        last_action_by = loadout.warehouse.security_gate_keeper if loadout.warehouse else loadout.collection_center.floor_supervisor

                    elif loadout.truck_status == "UNLOADED":
                        last_action_at = loadout.unload_at
                        last_action_by = loadout.warehouse.operation_officer if loadout.warehouse else loadout.collection_center.floor_supervisor

                single_data["action_by"] = f"{last_action_by.first_name} {last_action_by.last_name}"
                single_data["date_time"] = last_action_at
                data.append(single_data)

        return Response({"status": "success","message": "Successfully fetched the data.", "data":data},status=status.HTTP_200_OK)


class BuyingEmptyCratesView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanBuyingEmptyCratesPermission]
    serializer_class = BuyingEmptyCratesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        validated_data = serializer.validated_data
        return Response(
            {"status": "success", "message": "Successfully Crates added", "data":validated_data},
            status=status.HTTP_200_OK
        )
