from django.urls import path

from .views import warehouseViews, userViews

from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh token
    TokenRefreshView      # Refreshes access token
)



urlpatterns = [
    #User
    path('login', userViews.Login.as_view()),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]