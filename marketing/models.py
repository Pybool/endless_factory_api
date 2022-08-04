from django.db import models

from accounts.models import User
from products.models import Product, Variant
from django.core.exceptions import ValidationError

class Campaign(models.Model):
  campaign_name = models.CharField(max_length=100, default='N/A')
  listings = models.ManyToManyField(Product)
  variants = models.ManyToManyField(Variant)
  user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
  start_date = models.CharField(max_length=100,null=True, blank=True)
  end_date = models.CharField(max_length=100,null=True, blank=True)
  sold_id = models.CharField(max_length=100, default='N/A')
  ad_fees = models.CharField(max_length=100, default='N/A')
  sales = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  price_range = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  currency = models.CharField(max_length=32, null=True, blank=True, default='USD')
  paid = models.BooleanField(default=True)
  is_active = models.BooleanField(default=False)
  is_schedule = models.BooleanField(default=False)
  clicks = models.PositiveIntegerField(default=0)
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def clean(self):
      if self.start_date > self.end_date:
          raise ValidationError("Start date cannot be after end date")
  
  def __str__(self) -> str:
    return self.campaign_name