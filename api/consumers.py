import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Ride

class RideNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.room_group_name = f'ride_notifications_{self.driver_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_notification(self, event):
        message = event['message']
        ride_id = event['id']

        await self.send(text_data=json.dumps({
            'message': message,
            'ride_id': ride_id
        }))


class RideTrackingConsumer(AsyncJsonWebsocketConsumer):
    print('tracking')
    async def connect(self):
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.group_name = f"ride_tracking_{self.ride_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        latitude = content.get('latitude')
        longitude = content.get('longitude')

        if not latitude or not longitude:
            return

        await sync_to_async(Ride.objects.filter(id=self.ride_id).update)(
            latitude=latitude, longitude=longitude
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude,
            }
        )

    async def location_update(self, event):
        await self.send_json({
            'latitude': event['latitude'],
            'longitude': event['longitude']
        })