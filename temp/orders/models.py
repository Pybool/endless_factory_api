from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import itertools
from decimal import Decimal
from accounts.models import User, Address, CreditCard
from product.models import Variant
CURRENCY_OPTIONS = (
  ('USD', 'USD'),
)

class Cart(models.Model):
  token = models.CharField(unique=True, max_length=32)

  def total(self):
    total = 0
    for item in self.cartitem_set.all():
      item_price = item.price
      total += item_price
    return total
  
  def endless_factory_cut(self):
    ef_cut = (round(Decimal(self.total()), 2))

    return ef_cut if ef_cut <= 1500.0 else 0.0

  def grand_total(self):
    return (float(self.total())) + self.endless_factory_cut()

  def items_count(self):
    count = 0
    for item in self.cartitem_set.all():
      count += item.quantity
    return count

  def is_empty(self):
    return self.cartitem_set.count() == 0
  
  def cart_items(self):
    return self.cartitem_set.all()
  
  def reset(self):
    for cartitem in self.cartitem_set.all():
      cartitem.delete()
  
class CartItem(models.Model):
  cart = models.ForeignKey(Cart, default=None, on_delete=models.CASCADE)
  variant = models.ForeignKey(Variant, default=None, on_delete=models.CASCADE)
  option_value = models.CharField(max_length=100, default='N/A')
  option_type = models.CharField(max_length=100, default='N/A')

  quantity = models.IntegerField(validators=[MinValueValidator(1)], null=False, default=1)
  price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)

  def product(self):
    return self.variant.product

  def display_variant(self):
    return self.option_type + ": " + self.option_value

  def subtotal(self):
    return self.variant.price * self.quantity

class Order(models.Model):
  number = models.CharField(max_length=32, editable=False, null=False, unique=True)
  item_total = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  total = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  endless_factory_cut = models.DecimalField(validators=[MinValueValidator(0)], null=True, blank=True, default=0, decimal_places=2, max_digits=10)
  user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, blank=True, null=True)
  tracking_number = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipping_address', blank=True, null=True)
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)
  completed_at = models.DateTimeField(auto_now=True)
  special_instructions = models.TextField()
  is_shipped = models.BooleanField(default=False)
  is_cancelled = models.BooleanField(default=False)
  currency = models.CharField(null=False, editable=False, default='USD', max_length=32)

  def transaction(self):
    return self.transaction_set.first()

  def set_line_items_from_cart(self, cart):
    for item in cart.cartitem_set.all():
      option_type=item.variant.product.option_type.name
      option_value=item.variant.option_value.value
      line_item = LineItem(order = self, variant = item.variant, quantity = item.quantity, price = item.price, option_type=option_type, option_value=option_value)
      line_item.save()
      variant = line_item.variant
      variant.stock -= line_item.quantity
      variant.save()
  
  def set_transaction(self, user, charge, card_number, save_card):
    transaction = Transaction(order = self)
    transaction.transaction_id = charge['id']
    credit_card = user.credit_cards.filter(card_number=card_number).first()
    if credit_card != None:
      transaction.credit_card = credit_card
      transaction.save()
    else:
      credit_card = CreditCard(
        card_number=card_number,
        exp_month = charge['payment_method_details']['card']['exp_month'],
        exp_year = charge['payment_method_details']['card']['exp_year'],
        brand = charge['payment_method_details']['card']['brand'],
        name_on_card = charge['billing_details']['name']
      )
      credit_card.save()
      print(save_card)
      if save_card:
        user.credit_cards.add(credit_card)
      transaction.credit_card = credit_card
      transaction.save()

  def items_count(self):
    quantity = 0
    for item in self.lineitem_set.all():
      quantity += item.quantity
    return quantity

  def generate_number(self):
    last_order = Order.objects.last()
    number = "EF"+ str((last_order.id if last_order is not None else 0)+1).rjust(10, '0')
    self.number = number

  def save(self, *args, **kwargs):
    if not self.pk:
      self.generate_number()
    super().save(*args, **kwargs)

class Transaction(models.Model):
  order = models.ForeignKey(Order, default=None, on_delete=models.CASCADE)
  credit_card = models.ForeignKey(CreditCard, default=None, blank=True, on_delete=models.CASCADE, null=True)
  transaction_id = models.CharField(max_length=32, editable=False, null=False)

  def card_number_last_4(self):
    return self.credit_card.display_number()
  
  def card_brand(self):
    return self.credit_card.brand
  
  def card_expiry_month(self):
    return self.credit_card.exp_month
  
  def card_expiry_month(self):
    return self.credit_card.exp_month
  
  def card_expiry_year(self):
    return self.credit_card.exp_year

# Create your models here.
class LineItem(models.Model):
  order = models.ForeignKey(Order, default=None, on_delete=models.CASCADE)
  variant = models.ForeignKey(Variant, default=None, on_delete=models.CASCADE)
  dispatched = models.BooleanField(default=False)
  dispatched_at = models.DateTimeField(null=True, blank=True)
  option_value = models.CharField(max_length=100, default='N/A')
  option_type = models.CharField(max_length=100, default='N/A')
  courier_agency = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  tracking_number = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  quantity = models.IntegerField(validators=[MinValueValidator(0)], null=False, default=0)
  price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)

  def display_variant(self):
    return self.option_type + ": " + self.option_value

  def item_total(self):
    
    return (self.price)