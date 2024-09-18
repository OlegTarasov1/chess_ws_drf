from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import json
import random
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



class ActualChess(AsyncWebsocketConsumer):
    # amnt_users = set()

    # not yet figured out the algorithm of reconnect*

    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        game_meta = cache.get(self.room_group_name)

        if game_meta is None:
            await self.init_user_1()
        elif game_meta[1] is None:
            await self.init_user_2(game_meta[0]['side'])
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_meta',
                'message': game_meta
            }
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        if await self.is_your_turn(data['piece'].split('_')):
            if await self.is_possible(data): # not done yet
                previous_turn = cache.get(f'{self.room_group_name}_last_turn')
                user = cache.get(self.room_group_name)[1].remove(previous_turn[1])
                cache.set(f'{self.room_group_name}_last_turn', ['Black' if previous_turn[0] == 'White' else 'White', user, data], 60*10)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_meta',
                        'message': 'approve'
                    }
                )
            else:
                await self.send(json.dumps({
                    'message': 'you were not allowed to move the piece'
                }))

        else:
            await self.send(json.dumps({
                'message': 'you were not allowed to move the piece'
            }))

    async def is_your_turn(self, data):
        last_turn = cache.get(f'{self.room_group_name}_last_turn')
        users = cache.get(self.room_group_name)
        users.remove(last_turn[1])
        if last_turn[0] != data[0] and users[0]['tcp'] == self.scope['client']:
            return True
        else:
            return False

    async def is_possible(self): # not yet done
        pass




    async def init_user_1(self):
        user = self.scope['user']
        user1 = {
            'user': user.username if user.is_authenticated else 'Anonymous',
            'side': random.choice(['Black', 'White']),
            'tcp': self.scope['client']
        }
        user2 = None

        cache.set(self.room_group_name, [user1, user2])

        await self.send(json.dumps(user1))

    async def init_user_2(self, user_1_side):
        user = self.scope['user']
        user2 = {
            'user': user if user.is_authenticated else 'Anonymous',
            'side': 'Black' if user_1_side == 'White' else 'White',
            'tcp': self.scope['client']
        }

        meta_game = cache.get(self.room_group_name)
        meta_game[1] = user2
        cache.set(self.room_group_name, meta_game, 60*60)

        cache.set(f'{self.room_group_name}_last_turn', ['Black', meta_game[0] if meta_game[0]['side'] == 'Black'else meta_game[1]], 60*20)        

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_meta',
                'message': meta_game
            }
        )

    async def send_meta(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
