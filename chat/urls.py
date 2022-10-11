from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from django.conf import settings
from django.conf.urls.static import static
from .import views


urlpatterns = [
    path('chats/send_attachments/', views.ChatMessagesView.as_view(), name='message-detail'),
    # path('chats/messages/', views.ChatMessagesView.as_view(), name='message-list'),
    path('chats/users/<int:pk>', views.ChatUsersView.as_view(), name='user-detail'),
    path('chats/users/', views.ChatUsersView.as_view(), name='user-list'),
    path('chats/users/search/', views.ChatsSearchUsers.as_view(), name='search-user-list'),
    path('chats/messages_test/', views.MessageSendAPIView.as_view()),
    path('chats/get_chat_id/', views.GetChatUID.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

