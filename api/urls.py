from django.urls import path
from .views import LoginView, ActiveDriverListView, UpdateUserStatusView, CheckUserStatusView, CreateRideView, RideListView, UserRideListView, CancelRideView, AcceptRideView,\
CompleteRideView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('drivers/', ActiveDriverListView.as_view(), name='active-drivers'),
    path('update-status/', UpdateUserStatusView.as_view(), name='update-status'),
    path('check-status/', CheckUserStatusView.as_view(), name='check-status'),
    path('create_ride/', CreateRideView.as_view(), name='create_ride'),
    path('driver/rides/', RideListView.as_view(), name='ride-list'),
    path('user/rides/', UserRideListView.as_view(), name='user-ride-list'),
    path('cancel-ride/', CancelRideView.as_view(), name='cancel-ride'),
    path('accept-ride/', AcceptRideView.as_view(), name='accept-ride'),
    path('complete-ride/', CompleteRideView.as_view(), name='complete-ride'),

]