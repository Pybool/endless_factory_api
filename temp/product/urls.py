from django.contrib import admin
from django.conf.urls import url
from django.urls import path
import views

urlpatterns = [
    path('products', views.products),
    path('products/new_arrivals', views.new_arrivals_products),
    path('products/<slug:slug>', views.product),
]