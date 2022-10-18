import copy as ObjectCopy
from django.conf import settings
from chat.models import DocumentChatAttachment, ImageChatAttachment, VideoChatAttachment


class ChatHelper(object):
    
    def __init__(self,serializerData):
        
        self.all_chats = {}
        self.specific_chats = []
        self.media_attachments = []
        self.serializerData = serializerData
        
    def ParseUserchats(self):
        
        instance = None
        chats = set(sub['conversation'] for sub in self.serializerData)
        chat_ids = list(chats)

        for i in range(0,len(chat_ids)):
            
            for dic in self.serializerData:
            
                if chat_ids[i] == dic['conversation']:
                    if dic['attached_media_type'] == 'video':
                        instance = VideoChatAttachment.objects.filter(message_id=dic['id']).values("file")
                    
                    elif dic['attached_media_type'] == 'image':
                        instance = ImageChatAttachment.objects.filter(message_id=dic['id']).values("file")
                    
                    elif dic['attached_media_type'] == 'document':
                        instance = DocumentChatAttachment.objects.filter(message_id=dic['id']).values("file")
                    
                    if instance is not None:
                        for file in instance:
                            self.media_attachments.append(settings.SERVER_URL + ":" + settings.SERVER_PORT + settings.MEDIA_URL + str(file['file']))
                    dic['attached_media'] = ObjectCopy.deepcopy(self.media_attachments)
                    self.media_attachments.clear()
                    self.specific_chats.append(dic)
                    self.all_chats[chat_ids[i]] = ObjectCopy.deepcopy(self.specific_chats)
                    
            self.specific_chats.clear()

        return self.all_chats