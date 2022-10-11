
import json
import logging

from notifications.models import Notifications
log = logging.getLogger(__name__)
from accounts.authentication import JWTAuthenticationMiddleWare
from rest_framework.response import Response
from accounts.models import  User
from endless_factory_api.serializers import InboxSerializer
from rest_framework.views import APIView

class Inbox(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request): 
        
        notifications = Notifications.objects.filter(user=request.user).order_by('-id')[:100]
        serializer = InboxSerializer(notifications,many=True)   
        return Response({"status":True,"data":serializer.data})  
