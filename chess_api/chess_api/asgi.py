import os
from channels.routing import ProtocolTypeRouter, URLRouter 
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chess_app.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chess_api.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chess_app.routing.websocket_urlpatterns
        )
    )
})
