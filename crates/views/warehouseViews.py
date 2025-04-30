from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status


from ..serializers.warehouseSerializers import LoadEmptyCratesSerializer

class LoadEmptyCratesView(CreateAPIView):
    serializer_class = LoadEmptyCratesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Crates loaded successfully"}, status=status.HTTP_201_CREATED)
        
