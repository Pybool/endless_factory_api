from django.contrib import admin
from chat.models import Message, DocumentChatAttachment,ImageChatAttachment,VideoChatAttachment
admin.site.register(Message)
admin.site.register(DocumentChatAttachment)
admin.site.register(ImageChatAttachment)
admin.site.register(VideoChatAttachment)