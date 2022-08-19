from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('orders/cart/view_cart/<str:cart_token>', views.CartView.as_view()),
  path('orders/cart/checkout', views.CheckoutView.as_view()),
  path('orders/cart/add_to_cart', views.AddCartView.as_view()),
  path('orders/cart/remove_from_cart/<int:pk>', views.RemoveCartItemView.as_view()),
  path('orders/get_orders', views.OrdersView.as_view()),
  path('orders/log/testlogger', views.TestLogger.as_view()),
  
  

  
  

 ]
