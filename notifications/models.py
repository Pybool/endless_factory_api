from django.db import models
import logging

from orders.models import LineItem
log = logging.getLogger(__name__)
from accounts.models import User

class Notifications(models.Model):

  tracking_number = models.CharField(max_length=250,default='',blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE,null=False)
  item = models.ForeignKey(LineItem, on_delete=models.CASCADE,null=True)
  message = models.TextField(max_length=1500,default='')
  subject = models.CharField(max_length=250,default='N/A')
  created_at = models.DateTimeField()
  