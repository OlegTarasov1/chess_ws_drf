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
    amnt_users = set()

    # not yet figured out the algorithm of reconnect*
    async def connect(self):
        if len(self.amnt_users) + 1 > 2:
            await self.close()

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.add_group(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        self.amnt_users.add(self.channel_name)

        meta_game = cache.get(self.room_group_name)
        if meta_game == None:
            meta_game['user1'] = {
                'user': self.scope['user'],
                'side': random.choice(['Black', 'White'])
            }
            meta_game['user2'] = None
            meta_game['board'] = None

        elif meta_game['user2'] is None:
            user2 = {
                "user": self.scope['user'],
                'side': 'Black' if meta_game['user1']['side'] == 'White' else 'Black'
            }
        
        if meta_game['board'] == None:
            board = [['' for _ in range(1, 9)] for _ in range(1, 9)]
            
            for i in [2, 7]:
                for j in range(1, 9):
                    board[i][j] = f'{"B" if i == 2 else "W"}_pawn_{j}'

            board[1][1], board[1][8], board[8][1], board[8][8]  = 'B_rook_1', 'B_rook_8', 'W_rook_1', 'W_rook_8'
            board[1][2], board[1][7], board[8][2], board[8][7] = 'B_knight_2', 'B_knight_7', 'W_knight_2', 'W_knight_7'
            board[1][3], board[1][6], board[8][3], board[8][6] = 'B_bishop_3', 'B_bishop_6', 'W_bishop_3', 'W_bishop_6'
            board[1][4], board[1][5], board[8][4], board[8][5] = 'B_queen_4', 'B_king_5', 'W_queen_4', 'W_king_5'
            
            meta_game['board'] = board

        cache.set(self.room_group_name, [meta_game['user1'], meta_game['user2'], meta_game['board']], 60*60)
        



