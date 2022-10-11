# from chat.api.views import ConversationViewSet
from .api_router import urlpatterns
from django.urls import include, path
from chat.consumer import ChatConsumer, NotificationConsumer

websocket_urlpatterns = [
    path("chats/<metadata>/", ChatConsumer.as_asgi()),
    path("notifications/", NotificationConsumer.as_asgi()),
    
]

websocket_urlpatterns += urlpatterns