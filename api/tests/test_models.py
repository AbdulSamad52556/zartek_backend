from django.test import TestCase
from api.models import Ride
from django.contrib.auth import get_user_model

User = get_user_model()

class RideModelTest(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user(username="test_rider", password="password123")
        self.driver = User.objects.create_user(username="test_driver", password="password123")
        
        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_location="Location A",
            dropoff_location="Location B",
            status="requested",
        )

    def test_ride_creation(self):
        self.assertEqual(self.ride.status, "requested")
        self.assertEqual(self.ride.rider.username, "test_rider")
        self.assertEqual(self.ride.pickup_location, "Location A")

    def test_string_representation(self):
        self.assertEqual(str(self.ride), f"Ride {self.ride.id} ({self.ride.status})")
