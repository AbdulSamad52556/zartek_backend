from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Ride
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken

class RideAPITest(APITestCase):
    def setUp(self):
        self.rider = User.objects.create_user(username="rider1", password="password123", role='user')
        self.rider2 = User.objects.create_user(username="rider2", password="password123", role='user')
        self.driver = User.objects.create_user(username="driver1", password="password123", role='driver')
        self.driver2 = User.objects.create_user(username="driver2", password="password123", role='driver')

        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_location="Location A",
            dropoff_location="Location B",
            status="requested",
        )
        self.rider_token = self.get_jwt_token(self.rider)
        self.rider_token2 = self.get_jwt_token(self.rider2)
        self.driver_token = self.get_jwt_token(self.driver)
        self.driver_token2 = self.get_jwt_token(self.driver2)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate_as_driver2(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token2}')
    
    def authenticate_as_driver(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.driver_token}')

    def authenticate_as_rider(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.rider_token}')
    
    def authenticate_as_rider2(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.rider_token2}')

    def test_list_rides(self):
        self.authenticate_as_driver()
        response = self.client.get("/api/driver/rides/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0) 
        self.assertEqual(response.data[0]["id"], self.ride.id) 

    def test_cancel_ride_status(self):
        self.authenticate_as_driver()
        response = self.client.post(f"/api/cancel-ride/", {
            "ride_id": self.ride.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data['ride']["id"], self.ride.id)

    
    def test_accept_ride_status(self):
        self.authenticate_as_driver()
        response = self.client.post(f"/api/accept-ride/", {
            "ride_id": self.ride.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Ride accepted successfully")
        self.assertEqual(response.data["ride"], self.ride.id) 

        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'in_progress') 

    def test_complete_ride_status(self):
        self.authenticate_as_driver()
        self.ride.status = 'in_progress'
        self.ride.save()
        response = self.client.post(f"/api/complete-ride/", {
            "ride_id": self.ride.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Ride completed successfully")
        self.assertEqual(response.data["ride"],self.ride.id)

        self.ride.refresh_from_db()

    def test_create_ride(self):
        self.authenticate_as_rider2()
        response = self.client.post("/api/create_ride/", {
            "pickup_location": "Location X",
            "dropoff_location": "Location Y",
            "driver_id": self.driver2.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], response.data['id'])