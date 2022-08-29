from locale import currency
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import itertools
from decimal import Decimal

from accounts.models import User, Address, CreditCard
from orders.utils import ExchangeRate
from products.models import Product, Variant
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
  
  # def cost_prices(self):
  #   for item in self.cartitem_set.all():
  #     item_cost_price = item.cost_price
  #     total += item_price
  #   return total
  
  def endless_factory_cut(self):
    ef_cut = (round(Decimal(self.total()), 2))

    return ef_cut if ef_cut <= 1500.0 else 0.0

  def grand_total(self):
    return (Decimal(self.total())) #+ self.endless_factory_cut()

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
  product = models.ForeignKey(Product,null=True, default=None, on_delete=models.CASCADE)
  variant = models.ForeignKey(Variant, null=True, default=None, on_delete=models.CASCADE)
  option_value = models.CharField(max_length=100, default='N/A',null=True)
  option_type = models.CharField(max_length=100, default='N/A',null=True)
  quantity = models.IntegerField(validators=[MinValueValidator(1)], null=False, default=1)
  price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  cost_price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)

  def products(self):
    try:
      return self.variant.product
    except:
      return self.product
  
  def product_cost_price(self):
    try:
      return self.variant.product.cost_price
    except:
      return self.product.cost_price

  def display_variant(self):
    return self.option_type + ": " + self.option_value

  def subtotal(self):
    try:
      return self.variant.price * self.quantity
    except:
      return self.product.price * self.quantity

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
  cost_price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)

  def transaction(self):
    return self.transaction_set.first()

  def set_line_items_from_cart(self, cart,number,buyer):
    
    for item in cart.cartitem_set.all():
      try:
        business_source = item.variant.product.business_source
        option_type=item.variant.product.option_type.name
        option_value=item.variant.option_value.value
        line_item = LineItem(order = self,user = buyer, variant = item.variant, business_source=business_source, quantity = item.quantity, price = item.price, cost_price = item.cost_price, option_type=option_type, option_value=option_value,number=number)
        line_item.save()
        variant = line_item.variant
        variant.stock -= line_item.quantity
        variant.save()
      except:
        business_source = ""
        option_type=""
        option_value=""
        
        line_item = LineItem(order = self,user = buyer,product=item.product, variant = item.variant, business_source=business_source, quantity = item.quantity, price = item.price, cost_price = item.cost_price, option_type=option_type, option_value=option_value,number=number)
        line_item.save()
        # variant = line_item.variant
        # variant.stock -= line_item.quantity
        # variant.save()
  
  def set_transaction(self, user, charge, card_number, save_card, time_range):
    
    transaction = Transaction(order = self)
    transaction.customer = user
    transaction.transaction_id = charge['id']
    transaction.time_sent = time_range[0]
    transaction.time_arrived = time_range[1]
    transaction.amount = charge['amount']
    transaction.status = charge['paid']
    transaction.currency = charge['currency']
    transaction.receipt_url = charge['receipt_url']
    transaction.payment_method = charge['payment_method'].split("_")[0]
    exchange_rate_fee = ExchangeRate.get_exchange_rate_and_fee(charge)
    
    if exchange_rate_fee['status']:
      transaction.exchange_rate = exchange_rate_fee['exchange_rate']
      transaction.transaction_fee = exchange_rate_fee['transaction_fee']
    else:
      transaction.exchange_rate = 0.00
      transaction.transaction_fee = 0.00
      
    credit_card =   CreditCard.objects.filter(user=user,card_number=card_number).first()
    print(credit_card)
    if credit_card != None:
      transaction.credit_card = credit_card
      transaction.save()
    else:
      if save_card:
        credit_card = CreditCard(
        user_id = user.id,
        card_number=card_number,
        exp_month = charge['payment_method_details']['card']['exp_month'],
        exp_year = charge['payment_method_details']['card']['exp_year'],
        brand = charge['payment_method_details']['card']['brand'],
        name_on_card = charge['billing_details']['name']
      )
        credit_card.save()
        print(save_card)
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
    return number
  
  def save(self, *args, **kwargs):
    number = None
    if not self.pk:
      number = self.generate_number()
    super().save(*args, **kwargs)
    return number

class Transaction(models.Model):
  
  customer = models.ForeignKey(User, default=None, blank=False, on_delete=models.CASCADE, null=False)
  transaction_id = models.CharField(max_length=32, editable=False, null=False) #Stripe charge id
  time_sent = models.DateTimeField(null=True, blank=True)
  time_arrived = models.DateTimeField(null=True, blank=True)
  order = models.ForeignKey(Order, default=None, on_delete=models.CASCADE)
  credit_card = models.ForeignKey(CreditCard, default=None, blank=True, on_delete=models.CASCADE, null=True)
  payment_method = models.CharField(max_length=150, editable=False, null=False)
  currency = models.CharField(max_length=50, default="usd", editable=False, null=False)
  amount_paid = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=30)
  transaction_fee = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=20)
  exchange_rate = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  receipt_url = models.CharField(max_length=250, editable=False, null=True, blank=True)
  status = models.CharField(max_length=32, editable=False, null=True, blank=True)

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
  
  def get_customer_id_via_charge_id(self,charge_id):
    return self.objects.filter(transaction_id=charge_id).customer
  
# Create your models here.
class LineItem(models.Model):
  order = models.ForeignKey(Order, default=None, null=True, on_delete=models.CASCADE)
  variant = models.ForeignKey(Variant, default=None, null=True, on_delete=models.CASCADE)
  product = models.ForeignKey(Product, default=None, null=True, on_delete=models.CASCADE)
  user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
  dispatched = models.BooleanField(default=False)
  dispatched_at = models.DateTimeField(null=True, blank=True)
  option_value = models.CharField(max_length=100, default='N/A')
  option_type = models.CharField(max_length=100, default='N/A')
  courier_agency = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  tracking_number = models.CharField(max_length=32, null=True, blank=True, default='N/A')
  quantity = models.IntegerField(validators=[MinValueValidator(0)], null=False, default=0)
  price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  cost_price = models.DecimalField(validators=[MinValueValidator(0)], null=False, default=0, decimal_places=2, max_digits=10)
  business_source = models.CharField(max_length=250, default='N/A')
  order_status = models.CharField(max_length=100, default='N/A')
  number = models.CharField(max_length=100, default='N/A')
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)

  def display_variant(self):
    return self.option_type + ": " + self.option_value

  def item_total(self):
    return (self.price)
  
  def buyer_default_address(self):
    return (self.user.default_address())