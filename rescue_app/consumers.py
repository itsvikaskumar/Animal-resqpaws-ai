from channels.generic.websocket import AsyncWebsocketConsumer
import json


class AmbulanceTrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.tracking_id = self.scope["url_route"]["kwargs"]["tracking_id"]

        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connection",
            "message": "Live ambulance tracking connected",
            "tracking_id": self.tracking_id,
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") == "location_update":
            await self.send(text_data=json.dumps({
                "type": "location_update",
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            }))