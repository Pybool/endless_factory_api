from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('marketing/new_campaign', views.NewCampaignView.as_view()),
 ]
