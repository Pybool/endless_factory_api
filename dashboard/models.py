from locale import currency
from django.db import models
from django.core.validators import MinValueValidator

class Refunds(models.Model):
    
  customer = models.CharField(max_length=250, editable=False, null=False, blank=False)
  refund_id = models.CharField(max_length=250, editable=False, null=False)
  amount = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=20)
  currency = models.CharField(max_length=250,default='usd',null=True, blank=True)
  related_charge = models.CharField(max_length=250,null=False, blank=False)
  refund_reason = models.TextField(max_length=1000, editable=False, null=True, blank=True)
  status = models.CharField(max_length=32, editable=False, null=False, blank=False)
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)
  
