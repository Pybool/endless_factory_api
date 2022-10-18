from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('adsmarketing', views.NewCampaignView.as_view()), 
  path('adsmarketing/actions', views.CampaignActionsView.as_view()),
  path('adsmarketing/feeder', views.CampaignFeederView.as_view()),
  path('adsmarketing/clicks', views.CampaignAdsClick.as_view()),

  
  
 ]
