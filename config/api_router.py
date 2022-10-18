from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
import logging
log = logging.getLogger(__name__)
from chat.api.views import ConversationViewSet, MessageViewSet
# from user.api.views import UserViewSet

from django.conf.urls import url
from django.urls import path
from django.conf import settings
#from . import views


urlpatterns = [
    path('conversations/<metadata>/',ConversationViewSet.as_view()),
    
] 
log.info(urlpatterns[:1])