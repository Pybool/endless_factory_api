
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from .import views

urlpatterns = [
    path('single_product/<slug:slug>', views.SingleProduct.as_view()),
    path('products_listings', views.Products.as_view()),
    path('products/log/testlogger', views.TestLogger.as_view()),
    
]