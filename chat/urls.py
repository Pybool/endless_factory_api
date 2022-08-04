from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('chats/messages/<int:sender>/<int:receiver>/<int:pk>', views.ChatMessagesView.as_view(), name='message-detail'),
    path('chats/messages/', views.ChatMessagesView.as_view(), name='message-list'),
    path('chats/users/<int:pk>', views.ChatUsersView.as_view(), name='user-detail'),
    path('chats/users/', views.ChatUsersView.as_view(), name='user-list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 