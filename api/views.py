from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, LoginSerializer, RideSerializer, RideListSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, Ride
from rest_framework import status
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q

class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            try:
                user = authenticate(username=username, password=password)
            except Exception as e:
                print(e)
            if not user:
                return Response({"error": "Invalid credentials"}, status=400)

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "id": user.id,
                "role": user.role,
                "username": user.username
            })
        except Exception as e:
            print('issue')
            print(e)
            print('issue')
            return Response({
                "refresh": 'asdfasdf',
                "access": 'asdfasdf',
                "role": 'asdfasdf',
                "username": 'asdfasdf'
            })
        
class ActiveDriverListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        on_duty_drivers = CustomUser.objects.filter(role='driver', is_duty=True)
        drivers_without_requested_rides = on_duty_drivers.exclude(
            Q(ride_drives__status__in=['requested', 'in_progress'])
        )
        return drivers_without_requested_rides

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        drivers = queryset.values('id', 'username', 'email', 'role')
        return Response({"drivers": list(drivers)}, status=status.HTTP_200_OK)

class UpdateUserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        is_duty = request.data.get("is_active")
        if is_duty is None:
            return Response(
                {"error": "`is_active` field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(is_duty, bool):
            return Response(
                {"error": "`is_active` must be a boolean value."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_duty = is_duty
        user.save()

        status_message = "active" if user.is_duty else "inactive"
        return Response(
            {"message": f"User {user.username} is now {status_message}."},
            status=status.HTTP_200_OK
        )
    
class CheckUserStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user 
        return Response(
            {
                "username": user.username,
                "is_active": user.is_duty
            },
            status=status.HTTP_200_OK
        )
    
class CreateRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rider = request.user

        existing_ride = Ride.objects.filter(rider=rider, status__in=['requested', 'in_progress']).first()
        if existing_ride:
            return Response(
                {"error": "You already have a pending ride request."},
                status=status.HTTP_400_BAD_REQUEST
            )
        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response({"error": "Driver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = get_user_model().objects.get(id=driver_id, role='driver')
        except get_user_model().DoesNotExist:
            return Response({"error": "Driver not found or invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        pickup_location = request.data.get('pickup_location')
        dropoff_location = request.data.get('dropoff_location')

        ride = Ride.objects.create(
            rider=rider,
            driver=driver,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            status='requested'
        )

        ride_serializer = RideSerializer(ride)

        channel_layer = get_channel_layer()
        message = f"New ride request from {rider.username} at {pickup_location} to {dropoff_location}."
        async_to_sync(channel_layer.group_send)(
            f'ride_notifications_{driver_id}',
            {
                'type': 'send_notification',
                'message': message,
                'id': ride.id,
            }
        )

        return Response(ride_serializer.data, status=status.HTTP_201_CREATED)
    
class RideListView(generics.ListAPIView):
    serializer_class = RideListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        driver_id = self.request.user.id
        return Ride.objects.filter(driver_id=driver_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

class UserRideListView(generics.ListAPIView):
    serializer_class = RideListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        rider_id = self.request.user.id
        return Ride.objects.filter(rider_id=rider_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

class CancelRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ride_id = request.data.get('ride_id')
        if not ride_id:
            return Response({"error": "Ride ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ride = Ride.objects.get(id=ride_id)
        except Ride.DoesNotExist:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)
        if ride.status in ['cancelled', 'completed']:
            return Response({"error": "Ride cannot be cancelled, as it is already cancelled or completed"}, status=status.HTTP_400_BAD_REQUEST)
        
        ride.status = 'cancelled'
        ride.save()
        ride_serializer = RideSerializer(ride)

        return Response({"ride": ride_serializer.data}, status=status.HTTP_200_OK)

class AcceptRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ride_id = request.data.get('ride_id')

        if not ride_id:
            return Response({"error": "Ride ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ride = Ride.objects.get(id=ride_id)
            if ride.driver != request.user:
                return Response({"error": "You are not authorized to accept this ride"}, status=status.HTTP_403_FORBIDDEN)
            if ride.status in ['in_progress', 'completed', 'cancelled']:
                return Response({"error": "This ride has already been accepted or completed"}, status=status.HTTP_400_BAD_REQUEST)
            ride.status = 'in_progress'
            ride.save()
            return Response({"message": "Ride accepted successfully", "ride": ride.id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)

class CompleteRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ride_id = request.data.get('ride_id')

        if not ride_id:
            return Response({"error": "Ride ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ride = Ride.objects.get(id=ride_id)
            if ride.driver != request.user:
                return Response({"error": "You are not authorized to complete this ride"}, status=status.HTTP_403_FORBIDDEN)
            if ride.status != 'in_progress':
                return Response({"error": f"Ride cannot be completed in its current status: {ride.status}"}, status=status.HTTP_400_BAD_REQUEST)
            ride.status = 'completed'
            ride.save()
            return Response({"message": "Ride completed successfully", "ride": ride.id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)