from channels.generic.websocket import AsyncWebsocketConsumer
import json
from . models import Server

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class PacConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'pac_%s' % self.room_name

        servers = Server.objects.filter(serverName=self.room_name).first()
        print("Num of Players:", servers.numOfPlayers)

        if (servers.numOfPlayers >= 2):
            print("No buddy")
            servers.numOfPlayers += 1
            servers.save()
            #return home
            #return redirect('/home')
            return
        else:
            servers.numOfPlayers += 1
            servers.save()


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print("Oh yeah!")
        servers = Server.objects.filter(serverName=self.room_name).first()
        servers.numOfPlayers -= 1
        if (servers.numOfPlayers == 0):
            servers.delete()
        else:
            servers.save()


        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['pac_message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'pac_message',
                'pac_message': message
            }
        )

    # Receive message from room group
    async def pac_message(self, event):
        message = event['pac_message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'pac_message': message
        }))    