from accounts.models import User
from django.db import models

ATTACHMENT_TYPE_OPTIONS = (
  ('Image', 'Image'),
  ('Video', 'Video'),
  ('Document', 'document'),
)

class Message(models.Model):
     chat_uid = models.CharField(max_length=200, default='None')
     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')        
     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')        
     message = models.TextField(max_length=1500)
     timestamp = models.DateTimeField(auto_now_add=True)
     attached_media_type = models.CharField(max_length=200, default='video')
     is_read = models.BooleanField(default=False)
     is_favourite = models.BooleanField(default=False)
     
     def __str__(self):
           return self.message
       
     def chat_media(self):
        if self.attached_media_type=="image":
            images_paths = []
            for attachment in self.imagechatattachment_set.filter(attachment_type='Image'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    images_paths.append(attachment.file.url)
            return images_paths

        elif self.attached_media_type=="document":
            documents_paths = []
            for attachment in self.documentchatattachment_set.filter(attachment_type='Document'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    documents_paths.append(attachment.file.url)
            return documents_paths
        
        elif self.attached_media_type=="video":
            videos_paths = []
            for attachment in self.videochatattachment_set.filter(attachment_type='Video'):
                if attachment.file and hasattr(attachment.file, 'url'):
                    videos_paths.append(attachment.file.url)
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
  
  