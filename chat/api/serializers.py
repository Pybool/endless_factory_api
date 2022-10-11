from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Message, Conversation
from accounts.chatuser_serializer import UserSerializer
import logging
log = logging.getLogger(__name__)

# User = get_user_model()
from accounts.models import User

class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "to_user",
            "content",
            "timestamp",
            "read",
            "chat_media",
            "event"
        )
    
    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data

    def get_to_user(self, obj):
        return UserSerializer(obj.to_user).data
    


class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField(method_name='get_other_user')
    last_message = serializers.SerializerMethodField(method_name='get_last_message')

    class Meta:
        model = Conversation
        fields = ("id", "other_user", "last_message")

    def get_last_message(self, obj):
        print("Object ",obj)
        messages = obj[0].messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        try:
            if len(obj) > 0:
                log.info(f"Object new {obj[0]}")
                log.info(f"Object dir {dir(obj[0])}")
                emails = obj[0].name.split("#")
                log.info(f"emails {emails} {self.context}")
                context = {}
                for email in emails:
                    if email != self.context["user"].email:
                        # This is the other participant
                        log.info(f"Email to find {email}")
                        other_user = User.objects.get(email=email)
                        log.info("Other user"+ str(UserSerializer(other_user, context=context).data))
                        return UserSerializer(other_user, context=context).data
        except Exception as e:
            log.info(f"serilaier err {str(e)}")
            pass
