import json
from django.db.models import Q
from django.contrib.auth.models import User                                
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from chat.helper import ChatHelper
from chat.models import Message
from decorators import allowed_users  
from endless_factory_api.serializers import MessageAttachmentSerializer, MessageDownloadSerializer, MessageSerializer, ChatUserSerializer 

class ChatUsersView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()
    def get(self, request,pk=None): 
        """
        List all required messages, or create a new message.
        """
        if request.method == 'GET':
            if pk: 
                users = User.objects.filter(id=pk)[:100]
            else:
                users = User.objects.all()[:50]
            serializer = ChatUserSerializer(users, many=True, context={'request': request}) 
            return JsonResponse(serializer.data, safe=False)  
         
    @allowed_users()
    def post(self, request,pk=None): 
        
        if request.method == 'POST':
            data = JSONParser().parse(request)           # On POST, parse the request object to obtain the data in json
            serializer = ChatUserSerializer(data=data)        # Seraialize the data
            if serializer.is_valid():
                serializer.save()                                            # Save it if valid
                return JsonResponse(serializer.data, status=201)     # Return back the data on success
            return JsonResponse(serializer.errors, status=400)     # Return back the errors  if not valid
        
        
class ChatMessagesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()
    
    def get_object(self, pk):
        try:
            return Message.objects.filter(pk=2)
        except Message.DoesNotExist:
            pass

    def get(self,request, sender=None, receiver=None,pk=None):
        """
        List all required messages, or create a new message.
        """
        if request.method == 'GET':
            # messages = Message.objects.filter(sender_id=sender, receiver_id=receiver)
            user = request.user.id
            messages = Message.objects.filter(Q(receiver_id=user) | Q(sender_id=user)).order_by('-timestamp')
            serializer = MessageDownloadSerializer(messages, many=True, context={'request': request})
            self.chathelper = ChatHelper(serializer.data)
            data = self.chathelper.ParseUserchats()
            return JsonResponse(data, safe=False)
    
    def post(self,request, sender=None, receiver=None,pk=None):
        
        if request.method == 'POST':
            docs = ['documents']
            print(request.data['data'])
            data = json.loads(request.data['data'])
            serializer = MessageSerializer(data=data)
            print(serializer)
            if serializer.is_valid():
                instance = serializer.create(data)
                for doc in docs:
                    instance = self.saveAttachments(request,instance,data,request.FILES.getlist(doc, None))
                if instance:
                    pass
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
    
    def delete(self,request, sender=None, receiver=None,pk=None):
        message = self.get_object(pk)
        print(message)
        message.delete()
        return JsonResponse("Message and media was deleted successfully", safe=False)
        
    def saveAttachments(self,request,instance,data,files,doc=''):
        
        if request.method == 'POST':
            print("Files ",files,doc)
            data['message'] = str(instance.id)
            instance = MessageAttachmentSerializer(data=data,context={'documents': files})
            if instance.is_valid():
                return instance.create(data)