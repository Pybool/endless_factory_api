from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('ordertracking/track/', views.OrderTrackingView.as_view(), name='order-track'),
]