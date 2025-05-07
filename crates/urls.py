from django.urls import path, include
from .views import userViews,warehouseViews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh token
    TokenRefreshView      # Refreshes access token
)
urlpatterns = [
    path('login', userViews.Login.as_view()),
    path('loadCratesView', warehouseViews.LoadCratesView.as_view()),
    path('verifyTruckView/<int:pk>', warehouseViews.VerifyTruckView.as_view()),
    path('dispatchTruckView/<int:pk>', warehouseViews.DispatchTruckView.as_view()),
    path('entryCheckView/<int:pk>', warehouseViews.EntrycheckView.as_view()),
    path('exitcheckView/<int:pk>', warehouseViews.ExitcheckView.as_view()),
    path('unloadTruckView/<int:pk>', warehouseViews.UnloadTruckView.as_view()),
    path('cratesTracking',warehouseViews.CratesTracking.as_view()),
    path('emptyTruckEntryCheckView',warehouseViews.EmptyTruckEntryCheckView.as_view()),


    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),]