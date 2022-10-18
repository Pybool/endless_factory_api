import json
from django.contrib.auth import get_user_model
import logging
from accounts.models import UserProduct, User
from chat.api.serializers import ConversationSerializer
from products.models import Product, Variant
log = logging.getLogger(__name__)
from orders.models import LineItem
User = get_user_model()
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from chat.helper import ChatHelper
from chat.models import Conversation, Message
from decorators import allowed_users  
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from endless_factory_api.serializers import LineItemIndexSerializer, MessageAttachmentSerializer, MessageDownloadSerializer, MessageSerializer, ChatUserSerializer 

# http://165.232.185.232:8000/api/v1/chats/get_chat_id/?sender=${sender}&recepient=${recepient}

class GetChatUID(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]

    def get(self,request):
        
        self.sender = request.GET.get('sender')
        self.recepient = request.GET.get('recepient')
        
        self.chatters = [self.sender,self.recepient]
        self.chatters.sort()
        try:
            chat_id = Conversation.objects.filter(
                name__contains=self.chatters[0] + "#" + self.chatters[1]
            ).values('id')
            if chat_id !=None:
                return Response({'status':True,'chat_id':chat_id[0]})
        except:
            chat_id = False
            return Response({'status':True,'chat_id':chat_id})
        

class ConversationsViewSet(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"
    
    def get(self,request,chat_id):
    
        queryset = Conversation.objects.filter(
            name__contains=request.user.email
        )
        serializer = ConversationSerializer(data=queryset)
        print(serializer)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(str(serializer.data))

    def get_serializer_context(self):
        return {"request": self.request, "user": self.request.user}
    
    
class ChatUsersView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self, request,pk=None): 
      
        if request.method == 'GET':
            try:
                
                if pk: 
                    user = User.objects.filter(id=pk).values('id','name','email','user_type','company_name','phone_number','country')
                else:
                    users = []
                    admin_users = User.objects.filter(user_type='Admin').values('id','name','email','user_type','company_name','phone_number','country')
                    if request.user.is_buyer():
                        sellers_ordered_from_orders = LineItem.objects.select_related('variant','product').filter(order__user_id=request.user.id).values('product_id','variant_id')

                        product_ids = []
                        variant_ids = []
                        for item in list(sellers_ordered_from_orders):
                            for k,v in item.items():
                                if k == 'product_id' and v is not None:
                                    product_ids.append(v)
                                if k == 'variant_id' and v is not None:
                                    variant_ids.append(v)
                        log.info(str(set(product_ids)))
                        log.info(str(set(variant_ids)))
                        log.info("All "+str(sellers_ordered_from_orders))
                        u_ids = self.get_variants_product_user_ids(product_ids+variant_ids)
                        self.key = 'sellers'
                    
                    elif request.user.is_seller():
                        buyers_list = []
                        buyers = LineItem.objects.filter(business_source=request.user.company_name).values_list('user')
                        for item in list(buyers):
                            buyers_list.append(item[0])
                        
                        log.info(str("buyers ")+str(list(set(buyers_list))))
                        u_ids = list(set(buyers_list))
                        self.key = 'buyers'
                    for u_id in u_ids:
                        user = User.objects.filter(id=u_id).values('id','name','email','user_type','company_name','phone_number','country').first()
                        users.append(user)
                    log.warning(str('Users: ')+str(users))
                    return Response({self.key: users,'admin_users':admin_users, 'status': True})
                return Response({'user': user,'status': True})
            except Exception as e:
                log.error(str(e))
    
    def get_variants_product_ids(self,ids):
           p_ids = []
           for id in list(ids):
               p_id = Variant.objects.filter(product=id).values().first()
               p_ids.append(p_id)
           return p_ids
    
    def get_variants_product_user_ids(self,ids):
           p_ids = []
           for id in list(ids):
               instance = Product.objects.get(id=id)
               p_id = UserProduct.objects.filter(product=instance).values_list('user').first()
               p_ids.append(p_id[0])
           return list(set(p_ids))
       
    @allowed_users()
    def post(self, request,pk=None): 
        
        if request.method == 'POST':
            data = JSONParser().parse(request)           # On POST, parse the request object to obtain the data in json
            serializer = ChatUserSerializer(data=data)        # Seraialize the data
            if serializer.is_valid():
                serializer.save()  # Save it if valid
                return JsonResponse(serializer.data, status=201)     # Return back the data on success
            return JsonResponse(serializer.errors, status=400)     # Return back the errors  if not valid

class ChatsSearchUsers(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        q = request.GET.get('q','None')
        if request.method == 'GET':
            lookups =  Q(email__icontains=q) | Q(company_name__icontains=q) | Q(name__icontains=q) | Q(phone_number__icontains=q)
            users = User.objects.filter(lookups).values('id','name','email','user_type','company_name','phone_number','country') 
            return Response({'results': users,'status': True}) 
        
class ChatMessagesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()
    def get_object(self, pk):
        try:
            return Message.objects.filter(pk=pk)
        except Message.DoesNotExist:
            pass

    def get(self,request):
        """
        List all required messages, or create a new message.
        """
        pk = request.GET.get('pk')
        sender = request.GET.get('sender')
        receiver = request.GET.get('receiver')
        
        if request.method == 'GET':
            user = request.user.id
            messages = Message.objects.filter(Q(to_user_id=user) | Q(from_user_id=user)).order_by('-timestamp')
            serializer = MessageDownloadSerializer(messages, many=True, context={'request': request})
            self.chathelper = ChatHelper(serializer.data)
            data = self.chathelper.ParseUserchats()
            return Response({'conversation_thread':data,'chat_uid':data.keys() ,'status': True}) 
    
    def post(self,request):
        # [chat_uid,sender,receiver,content,event]
        if request.method == 'POST':
            docs = ['documents']
            log.info(request.data['data'])
            data = json.loads(request.data['data'])
            
            if str(data.get('sender')) != str(request.user.email):
                return Response({'Message':'You cant send a message with another users account','status': False})
           
            data['from_user'] = User.objects.get(email=data['sender'])
            data['to_user'] = User.objects.get(email=data['receiver'])
            log.info(str(data['from_user']) + str([data['to_user']]))
            
            msg_instance = self.create(data,docs)
            for doc in docs:
                print("Request.Files ",request.FILES.getlist(doc, None))
                self.saveAttachments(request,msg_instance,data,request.FILES.getlist(doc, None))
            
            if msg_instance:
                return Response({'message_id':msg_instance.id ,'status': True}) 
            else:
                return Response({'message':"Something went wrong..." ,'status': False}) 
    
    def create(self,validated_data,docs):
    
      with transaction.atomic():
       
        chat_uid = validated_data['chat_uid']        
        validated_data['from_user'] = User.objects.get(email=validated_data['sender'])
        validated_data['to_user'] = User.objects.get(email=validated_data['receiver'])
        log.info(validated_data['receiver'] + "#" + validated_data['sender'])
        created = False
        
        try:
          self.conversation = Conversation.objects.get(
                  name= validated_data['receiver'] + "#" + validated_data['sender']
              )
          created = True
          log.info(f"self.conversation 1 {self.conversation}")
          
        except Exception as e:
          self.conversation = Conversation.objects.get(
                  name= validated_data['sender'] + "#" + validated_data['receiver']
              )
          created = True
          log.info(f"self.conversation 2 {self.conversation}")
          
        if created:
            Conversation.objects.filter(name=validated_data['receiver'] + "#" + validated_data['sender']).update(id=validated_data['chat_uid'])

        validated_data['conversation'] = self.conversation
        log.info(f"{validated_data}")
        validated_data.pop("chat_uid")
        validated_data.pop('sender')
        validated_data.pop('receiver')
        
        try:
          instance = Message.objects.create(**validated_data)
          instance.save()
        except:
          pass
       
        return instance
    
    def delete(self,request, sender=None, receiver=None,pk=None):
        message = self.get_object(pk)
        message.delete()
        return JsonResponse("Message and media was deleted successfully", safe=False)
        
    def saveAttachments(self,request,instance,data,files,doc=''):
        
        if request.method == 'POST':
            print("Files ",files,doc)
            
            data['message'] = str(instance.id)
            instance = MessageAttachmentSerializer(data=data,context={'documents': files})
            if instance.is_valid():
                return instance.create(data)

class MessageSendAPIView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]    

    def get(self, request):
        log.info(request.user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "general", {"type": "send_info_to_user_group",
                        "text": {"status": "done"}}
        )
        return Response({"status": True}, status=status.HTTP_200_OK)         

class MessageSendAPIView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]    

    def get(self, request):
        log.info(request.user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "general", {"type": "send_info_to_user_group",
                        "text": {"status": "done"}}
        )
        return Response({"status": True}, status=status.HTTP_200_OK)

    def post(self, request):
        socket_message = f"Message with id was created!"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{request.user.id}-message", {"type": "send_last_message",
                                           "text": socket_message}
        )
        return Response({"status": True}, status=status.HTTP_201_CREATED)