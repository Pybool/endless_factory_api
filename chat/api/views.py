import json
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from accounts.authentication import JWTAuthenticationMiddleWare
from rest_framework.views import APIView
from ..models import Conversation, Message
from ..api.paginaters import MessagePagination
from rest_framework.response import Response
from .serializers import MessageSerializer, ConversationSerializer
import logging
log = logging.getLogger(__name__)

class ConversationViewSet(APIView):

    authentication_classes = [JWTAuthenticationMiddleWare]
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = "name"

    def get(self,request,metadata):
        log.info(f"THe view metadata {metadata} and type {type(metadata)}")
        metadata = str(json.loads(metadata).get("chat_id")).replace("-","")
        try:
            queryset = Conversation.objects.filter(
                id__contains=metadata
            )
            self.get_serializer_context(request)
            serializer = ConversationSerializer(queryset,context={'user': request.user})
        
            return Response(serializer.data)
        except Exception as e:
            return Response(queryset.values())

    def get_serializer_context(self,request):
        return {"request": request, "user": request.user}


class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_name = self.request.GET.get("conversation")
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.username,
            )
            .filter(conversation__name=conversation_name)
            .order_by("-timestamp")
        )
        return queryset
