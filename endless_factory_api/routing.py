import os

from chat.middlewares import WebSocketJWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from config import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endless_factory_api.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": WebSocketJWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
    }
)
