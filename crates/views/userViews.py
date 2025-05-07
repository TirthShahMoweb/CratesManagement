from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers.userSerializers import LoginSerializer



class Login(CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(mobile_number = data['mobile_number']).first()
        refresh = RefreshToken.for_user(user)
        data = {"refresh": str(refresh),
                "access": str(refresh.access_token),
                "mobile_number": user.mobile_number,
                "username": user.username}
        return Response({"status":"Success", "message":"Successfully Logged In.", "data":data}, status=status.HTTP_200_OK)