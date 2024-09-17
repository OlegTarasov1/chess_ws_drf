from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import json
import asyncio


class ChessChat(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        group_messages = cache.get(self.room_group_name)
        if group_messages != None:
            for i in group_messages:
                await self.chat_message(i)


    async def disconnect(self, code):
        await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']

        cached = cache.get(self.room_group_name) if cache.get(self.room_group_name) is not None else []
        cached.append({
            'user': user.username,
            'message': data['message']
        })
        cache.set(self.room_group_name, cached, 60*60)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'user': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(json.dumps({
            'message': event['message'],
            'user': event['user']
        }))