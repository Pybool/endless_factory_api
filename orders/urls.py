from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('orders/cart/view_cart/<str:cart_token>', views.CartView.as_view()),
  path('orders/cart/checkout', views.CheckoutView.as_view()),

 ]
