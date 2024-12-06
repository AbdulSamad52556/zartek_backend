from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Ride
from .models import CustomUser
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password':{"write_only": True}}
    
    def create(self, validate_data):
        user = CustomUser.objects.create_user(
            username=validate_data['username'],
            email=validate_data['email'],
            password=validate_data['password'],
            role=validate_data['role']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        print("Received username: ", data['username'])
        user = authenticate(**data)
        if user and user.is_active:
            print("User authenticated: ", user)
            return user
        print("Authentication failed")
        raise serializers.ValidationError("Invalid credentials.")
    
class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'

class RideListSerializer(serializers.ModelSerializer):
    rider_username = serializers.CharField(source="rider.username", read_only=True)
    driver_username = serializers.CharField(source="driver.username", read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id",
            "pickup_location",
            "dropoff_location",
            "status",
            "created_at",
            "updated_at",
            "rider_username",
            "driver_username",
        ]