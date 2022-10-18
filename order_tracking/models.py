from django.db import models
import logging
log = logging.getLogger(__name__)

ORDER_TRACKING_CHOICES = ( 
    ("Pending", "Pending"), 
    ("Processing", "Processing"), 
    ("Dispatched", "Dispatched"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    
)


class OrderTracking(models.Model):

  tracking_number = models.CharField(max_length=250,default='',unique=True)
  order_created_at = models.CharField(max_length=250,default='')
  processed_at = models.CharField(max_length=250,default='')
  processing_comment = models.CharField(max_length=250,default='')
  dispatched_at = models.CharField(max_length=250,default='')
  dispatched_comment = models.CharField(max_length=250,default='')
  shipped_at = models.CharField(max_length=250,default='')
  shipping_comment = models.CharField(max_length=250,default='')
  delivered_at = models.CharField(max_length=250,default='')
  delivery_comment = models.CharField(max_length=250,default='')
  active_status = models.CharField(max_length=500, choices=ORDER_TRACKING_CHOICES, default='Pending')
  