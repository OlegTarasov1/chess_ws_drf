from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/v1/<room_name>/', consumers.ChessChat.as_asgi())
]