


import json
import logging
from uuid import UUID
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer
from .api.serializers import MessageSerializer
from .models import Conversation, Message
log = logging.getLogger(__name__)
User = get_user_model()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.chatters = None
        self.conversation_name = None
        self.conversation = None
        self.message_id = '0'

    def connect(self):
        self.user = self.scope["user"]
        log.info(f"URL PARAMS {self.scope}")
        if not self.user.is_authenticated:
            return

        self.accept()
        self.conversation_name = (f"{json.loads(self.scope['url_route']['kwargs']['metadata'])['chat_id']}").replace("-","")
        self.sender = (f"{json.loads(self.scope['url_route']['kwargs']['metadata'])['sender']}")
        self.recepient = (f"{json.loads(self.scope['url_route']['kwargs']['metadata'])['recepient']}")
        self.chatters = [self.sender,self.recepient]
        self.chatters.sort()
        log.info(f"Chatters {self.chatters}")
        
        try:
            self.message_id = (f"{json.loads(self.scope['url_route']['kwargs']['metadata'])['message_id']}")
        except:
            self.message_id = '0'

        try:
            self.conversation, created = Conversation.objects.get_or_create(
                name= self.chatters[0] + "#" + self.chatters[1]
            )
            if created:
                log.info(f"Created new chat {created}")
                Conversation.objects.filter(name=self.chatters[0] + "#" + self.chatters[1]).update(id=self.conversation_name)

            async_to_sync(self.channel_layer.group_add)(
                self.conversation_name,
                self.channel_name,
            )
            self.send_json(
                {
                    "type": "online_user_list",
                    "users": [user.username for user in self.conversation.online.all()],
                }
            )
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "user_join",
                    "user": self.user.username,
                },
            )
            self.conversation.online.add(self.user)

            messages = self.conversation.messages.all().order_by("-timestamp")[0:10]
            message_count = self.conversation.messages.all().count()
            self.send_json(
                {
                    "type": "last_50_messages",
                    "messages": MessageSerializer(messages, many=True).data,
                    "has_more": message_count > 5,
                }
            )
        except Exception as e:
            log.info(f"An error occured {str(e)}")
            
            
    def disconnect(self, code):
        if self.user.is_authenticated:
            # send the leave event to the room
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "user_leave",
                    "user": self.user.username,
                },
            )
            self.conversation.online.remove(self.user)
        return super().disconnect(code)

    def get_receiver(self):
        try:
            email = self.sender
          
            if email != self.user.email:
                # This is the receiver
                return User.objects.get(email=email)
        
        except Exception as e:
            log.info(f"Get receiver  error occured {str(e)}")
            
    def receive_json(self, content,**kwargs):
        try:
            message_type = content["type"]
            message_id = content.get('message_id') or '0'
            event = content.get('event')
            event = 'text' if event != 'nda' else event

            if message_type == "read_messages":
                messages_to_me = self.conversation.messages.filter(to_user=self.user)
                messages_to_me.update(read=True)

                # Update the unread message count
                unread_count = Message.objects.filter(to_user=self.user, read=False).count()
                async_to_sync(self.channel_layer.group_send)(
                    self.user.username + "__notifications",
                    {
                        "type": "unread_count",
                        "unread_count": unread_count,
                    },
                )

            if message_type == "typing":
                async_to_sync(self.channel_layer.group_send)(
                    self.conversation_name,
                    {
                        "type": "typing",
                        "user": self.user.username,
                        "typing": content["typing"],
                    },
                )

            if message_type == "chat_message":
                
                if message_id == '0':
                    message = Message.objects.create(
                        from_user=self.user,
                        to_user=self.get_receiver(),
                        content=content["message"],
                        conversation=self.conversation,
                        event=event
                    )
                else:
                    message_id = message_id.replace("-",'')
                    message = Message.objects.get(id=message_id)
                    
                async_to_sync(self.channel_layer.group_send)(
                    self.conversation_name,
                    {
                        "type": "chat_message_echo",
                        "name": self.user.username,
                        "message": MessageSerializer(message).data,
                    },
                )

                notification_group_name = self.get_receiver().username + "__notifications"
                async_to_sync(self.channel_layer.group_send)(
                    notification_group_name,
                    {
                        "type": "new_message_notification",
                        "name": self.user.username,
                        "message": MessageSerializer(message).data,
                    },
                )

            return super().receive_json(content, **kwargs)
        
        except Exception as e:
            log.info(f"Receive json error occured {str(e)}")

    def chat_message_echo(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 1 action error occured {str(e)}")

    def user_join(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 2 action error occured {str(e)}")

    def user_leave(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 3 action error occured {str(e)}")

    def typing(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 4 action error occured {str(e)}")

    def new_message_notification(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 5 action error occured {str(e)}")

    def unread_count(self, event):
        try:
            self.send_json(event)
        except Exception as e:
            log.info(f"Send json 6 action error occured {str(e)}")

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncoder)


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.notification_group_name = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()

        # private notification group
        self.notification_group_name = self.user.username + "__notifications"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

        # Send count of unread messages
        unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_count,
            }
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)