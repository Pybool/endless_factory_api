import os,uuid
from accounts.models import User
from django.db import models
from django.contrib.auth import get_user_model
# User = get_user_model()

ATTACHMENT_TYPE_OPTIONS = (
  ('image', 'image'),
  ('video', 'video'),
  ('document', 'document'),
)

class Room(models.Model):
  
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.title

    @property
    def group_name(self):
        return "room-%s" % self.id

class Conversation(models.Model):
    id = models.CharField(primary_key=True,max_length=250, default='', editable=False)
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=User, blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"
    
class Message(models.Model):
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages",null=True)
     from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender',null=True)        
     to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver',null=True)        
     message = models.TextField(max_length=1500,default='')
     timestamp = models.DateTimeField(auto_now_add=True)
     attached_media_type = models.CharField(max_length=200, default='Image')
     is_read = models.BooleanField(default=False)
     is_favourite = models.BooleanField(default=False)
     content = models.CharField(max_length=512,default='')
     timestamp = models.DateTimeField(auto_now_add=True)
     read = models.BooleanField(default=False)
     event = models.CharField(max_length=512,default='text')
     
    #  def __str__(self):
    #        return self.message
       
     def chat_media(self):
        print("attachment type ",self.attached_media_type, self.imagechatattachment_set.filter(attachment_type='image'))
        if self.attached_media_type=="image":
            images_paths = []
            for attachment in self.imagechatattachment_set.filter(attachment_type='image'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    file_size = os.path.getsize('/var/www/endless_factory_api/media_root'+attachment.file.url)
                    print("File size ", file_size)
                    images_paths.append({"url":attachment.file.url,"file_size":file_size / (1024 * 1024)})
            print("Images path ",images_paths)
            
            return tuple(images_paths)

        elif self.attached_media_type=="document":
            documents_paths = []
            for attachment in self.documentchatattachment_set.filter(attachment_type='document'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    # documents_paths.append(attachment.file.url)
                    file_size = os.path.getsize('/var/www/endless_factory_api/media_root'+attachment.file.url)
                    print("File size ", file_size)
                    documents_paths.append({"url":attachment.file.url,"file_size":file_size / (1024 * 1024)})
            return documents_paths
        
        elif self.attached_media_type=="video":
            videos_paths = []
            for attachment in self.videochatattachment_set.filter(attachment_type='video'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    videos_paths.append(attachment.file.url)
                    file_size = os.path.getsize('/var/www/endless_factory_api/media_root'+attachment.file.url)
                    print("File size ", file_size)
                    videos_paths.append({"url":attachment.file.url,"file_size":file_size / (1024 * 1024)})
            return videos_paths
    
     class Meta:
           ordering = ('timestamp',)


class DocumentChatAttachment(models.Model):
  message = models.ForeignKey(Message, default=None, on_delete=models.DO_NOTHING)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Document')
  file = models.FileField(upload_to='chat_attachments/documents/%Y/%m/%d/', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None

class ImageChatAttachment(models.Model):
  message = models.ForeignKey(Message, default=None, on_delete=models.DO_NOTHING)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Image')
  file = models.FileField(upload_to='chat_attachments/images/%Y/%m/%d/', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None

class VideoChatAttachment(models.Model):
  message = models.ForeignKey(Message, default=None, on_delete=models.DO_NOTHING)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Video')
  file = models.FileField(upload_to='chat_attachments/videos/%Y/%m/%d/', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None
  
  