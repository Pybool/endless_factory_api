from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import PermissionsMixin
# from django.contrib.auth.models import User

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

import datetime
from products.models import Variant, Product

# Create your models here.
ENTITY_TYPE_CHOICES = ( 
    ("LLC", "LLC"), 
    ("Corporation", "Corporation"), 
    ("Sole Proprietor", "Sole Proprietor")
)

COUNTRY_CHOICES = (
    ("Albania", "Albania"),("Nigeria", "Nigeria"), ("Algeria", "Algeria"), ("Angola", "Angola"), ("Argentina", "Argentina"), ("Armenia", "Armenia"), ("Australia", "Australia"), ("Austria", "Austria"), ("Azerbaijan", "Azerbaijan"), ("Bahamas", "Bahamas"), ("Bahrain", "Bahrain"), ("Bangladesh", "Bangladesh"), ("Barbados", "Barbados"), ("Belarus", "Belarus"), ("Belgium", "Belgium"), ("Belivia", "Belivia"), ("Belize", "Belize"), ("Benin", "Benin"), ("Bosnia", "Bosnia"), ("Botswana", "Botswana"), ("Brazil", "Brazil"), ("Brunei", "Brunei"), ("Bulgaria", "Bulgaria"), ("Camaroon", "Camaroon"), ("Cambodia", "Cambodia"), ("Canada", "Canada"), ("Chile", "Chile"), ("Colombia", "Colombia"), ("Costa Rica", "Costa Rica"), ("Cote D'ivoire", "Cote D'ivoire"), ("Croatia", "Croatia"), ("Cyprus", "Cyprus"), ("Czech Repub", "Czech Repub"), ("Denmark", "Denmark"), ("Dominican Repub", "Dominican Repub"), ("Ecuador", "Ecuador"), ("Egypt", "Egypt"), ("El Salvador", "El Salvador"), ("Estonia", "Estonia"), ("Ethiopia", "Ethiopia"), ("Fiji", "Fiji"), ("Finland", "Finland"), ("France", "France"), ("Georgia", "Georgia"), ("Germany", "Germany"), ("Ghana", "Ghana"), ("Greece", "Greece"), ("Grenada", "Grenada"), ("Guatemala", "Guatemala"), ("Guinea", "Guinea"), ("Guyana", "Guyana"), ("Haiti", "Haiti"), ("Honduras", "Honduras"), ("Hungary", "Hungary"), ("Iceland", "Iceland"), ("India", "India"), ("Indonesia", "Indonesia"), ("Ireland", "Ireland"), ("Israel", "Israel"), ("Italy", "Italy"), ("Jamaica Mon", "Jamaica Mon"), ("Japan", "Japan"), ("Jordan", "Jordan"), ("Kazakhstan", "Kazakhstan"), ("Kenya", "Kenya"), ("Kuwait", "Kuwait"), ("Kyrgyzstan", "Kyrgyzstan"), ("Laos", "Laos"), ("Latvia", "Latvia"), ("Lebanon", "Lebanon"), ("Lesotho", "Lesotho"), ("Liberia", "Liberia"), ("Libya", "Libya"), ("Lithuania", "Lithuania"), ("Luxembourg", "Luxembourg"), ("Madagascar", "Madagascar"), ("Malawi", "Malawi"), ("Malaysia", "Malaysia"), ("Maldives", "Maldives"), ("Malta", "Malta"), ("Mauritania", "Mauritania"), ("Mauritius", "Mauritius"), ("Mexico", "Mexico"), ("Moldova", "Moldova"), ("Mongolia", "Mongolia"), ("Montenegro", "Montenegro"), ("Morocco", "Morocco"), ("Myanmar", "Myanmar"), ("N Macedonia", "N Macedonia"), ("Namibia", "Namibia"), ("Nepal", "Nepal"), ("Netherlands", "Netherlands"), ("New Zealand", "New Zealand"), ("Nicaragua", "Nicaragua"), ("Niger", "Niger"), ("Norway", "Norway"), ("Oman", "Oman"), ("Pakistan", "Pakistan"), ("Palestine", "Palestine"), ("Panama", "Panama"), ("Papua New Guinea", "Papua New Guinea"), ("Paraguay", "Paraguay"), ("Peru", "Peru"), ("Philippines", "Philippines"), ("Poland", "Poland"), ("Portugal", "Portugal"), ("Qatar", "Qatar"), ("Romania", "Romania"), ("Rwanda", "Rwanda"), ("Samoa", "Samoa"), ("Saudi Arabia", "Saudi Arabia"), ("Senegal", "Senegal"), ("Serbia", "Serbia"), ("Seychelles", "Seychelles"), ("Sierra Leon", "Sierra Leon"), ("Singapore", "Singapore"), ("Slovakia", "Slovakia"), ("Slovenia", "Slovenia"), ("Somalia", "Somalia"), ("South Africa", "South Africa"), ("South Korea", "South Korea"), ("Spain", "Spain"), ("Sri Lanka", "Sri Lanka"), ("St Kitts/Nevis", "St Kitts/Nevis"), ("St Vince & The Gs", "St Vince & The Gs"), ("Suriname", "Suriname"), ("Sweden", "Sweden"), ("Switzerland", "Switzerland"), ("Tajikistan", "Tajikistan"), ("Tanzania", "Tanzania"), ("Thailand", "Thailand"), ("Togo", "Togo"), ("Trinidad & Tobago", "Trinidad & Tobago"), ("Tunisia", "Tunisia"), ("Turkmenistan", "Turkmenistan"), ("Uae", "Uae"), ("Uganda", "Uganda"), ("Ukraine", "Ukraine"), ("United Kingdom", "United Kingdom"), ("United States", "United States"), ("Uruguay", "Uruguay"), ("Uzbekistan", "Uzbekistan"), ("Vietnam", "Vietnam"), ("Zambia", "Zambia"), ("Zimbabwe", "Zimbabwe")
)

USER_TYPE_CHOICES = ( 
    ("Seller", "Seller"), 
    ("Buyer", "Buyer"), 
    ("Admin", "Admin"),
    ("Both", "Both"),
    
)

ATTACHMENT_TYPE_OPTIONS = (
  ('Image', 'Image'),
  ('Video', 'Video'),
)
    
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('user_type', 'Buyer')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('user_type', 'Admin')

        if extra_fields.get('user_type') != 'Admin':
            raise ValueError('Superuser must have user_type=Admin.')

        user =  self._create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class User(AbstractBaseUser,PermissionsMixin):
    """User model."""
    username = models.CharField(max_length=255, null=False, default='Name N/A')
    name = models.CharField(max_length=255, null=False, default='Name N/A')
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES, default='Buyer')

    bio=models.TextField(blank=True, default='N/A')

    #Seller Account Info
    company_name=models.CharField(max_length=200, blank=True)
    account_manager_name = models.CharField(max_length=250, blank=True)
    account_manager_phone_1 = models.CharField(max_length=200, blank=True)
    account_manager_phone_2 = models.CharField(max_length=200, blank=True) 
    company_mailing_address = models.EmailField(max_length=100, blank=True)
    referrer_email = models.EmailField(verbose_name='email address', max_length=255, null=True, blank=True)
    has_existing_shop =  models.BooleanField(default=False)
    store_name = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)
    company_address_1 = models.CharField(max_length=200, blank=True)
    company_address_2 = models.CharField(max_length=200, blank=True)
    company_postal_code = models.CharField(max_length=250, blank=True)
    city_location = models.CharField(max_length=250, blank=True)
    company_ceo_name = models.CharField(max_length=250, blank=True)
    biz_info_submitted = models.BooleanField(default=False)
    biz_info_verified = models.BooleanField(default=False)
    contact_preferences = models.TextField(blank=True)
    
    # company_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='company_address', blank=True, null=True)
    country = models.CharField(max_length=255, null=False, choices=COUNTRY_CHOICES, default='United States')

    tax_id_number=models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    entity_type=models.CharField(max_length=100, choices=ENTITY_TYPE_CHOICES, default='LLC', blank=True)
    payment_acceptance_type = models.CharField(max_length=100, blank=True)
    bank_info = models.TextField(blank=True)
    number_of_employees = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10000000)], blank=True)
    year_founded = models.PositiveIntegerField(default=current_year(), validators=[MinValueValidator(1900), max_value_current_year], blank=True)
    gross_annual_revenue = models.DecimalField(decimal_places=2, max_digits=9, default=0, blank=True)
    # default_address = models.JSONField(Address.objects.filter(user=id).values().first())
    
    avatar = models.FileField(upload_to='user_avatar', null=True, blank=True)
    otp = models.IntegerField(blank=True, validators=[MinValueValidator(100000), MaxValueValidator(999999)], default=None, null=True)
    otp_expires_at = models.DateTimeField(auto_now=True)
    cart_token = models.CharField(max_length=100, blank=True, null=True)
    
    is_verified_account = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def is_admin(self):
        return self.user_type == 'Admin'

    def is_buyer(self):
        return self.user_type == 'Buyer'
    
    def is_seller(self):
        return self.user_type == 'Both'
    
    def is_info_submitted(self):
        return self.biz_info_submitted
    
    def is_info_verified(self):
        return self.biz_info_verified

    def wishlisted_products(self):
        products = []
        for wishlisted_product in self.wishlistedproduct_set.all():
            products.append(wishlisted_product.product)
        return products

    def shipping_addresses(self):
        return Address.objects.filter(user=self.id).values()
    
    def default_address(self):
        return Address.objects.filter(user=self.id).values().first()
    
    def credit_cards_count(self):
        return self.credit_cards.count()
        
    def has_reviewed_the_product(self, product_id):
        return Review.objects.filter(user=self, product_id=product_id).count() > 0
    
    def idcard_images(self):
        images_paths = []
        for attachment in self.idcardsattachment_set.filter(attachment_type='Image'):
            if attachment.file and hasattr(attachment.file, 'url'):
                images_paths.append(attachment.file.url)
        return images_paths

    def pba_images(self):
        images_paths = []
        for attachment in self.proofbusinessattachment_set.filter(attachment_type='Image'):
            if attachment.file and hasattr(attachment.file, 'url'):
                images_paths.append(attachment.file.url)
        return images_paths

    def products(self):
        products = []
        for user_product in self.userproduct_set.all():
            products.append(user_product.product)
        return products

class IDCardsAttachment(models.Model): 
  company = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Image')
  file = models.FileField(upload_to='id_cards_attachments/%Y/%m/%d/', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None

class ProofBusinessAttachment(models.Model):
  company = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Image')
  file = models.FileField(upload_to='business_ownership_attachments/%Y/%m/%d/', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None
  
  
class Address(models.Model):
    user =  models.ForeignKey(User,default=None, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=False, default='N/A')
    last_name = models.CharField(max_length=255, null=False, default='N/A')
    line_1 = models.CharField(max_length=255, null=False, default='N/A')
    line_2 = models.CharField(max_length=255, null=True, blank=True, default='N/A')
    city = models.CharField(max_length=255, null=False, default='N/A')
    zipcode = models.CharField(max_length=255, null=False, default='N/A')
    state = models.CharField(max_length=255, null=False, default='N/A')
    country = models.CharField(max_length=255, null=False, choices=COUNTRY_CHOICES, default='United States')
    is_shipping_address = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class CreditCard(models.Model):
    user = models.ForeignKey(User,default=None, on_delete=models.CASCADE)
    card_number = models.CharField(null=False, max_length=20)
    brand = models.CharField(null=True, blank=True, max_length=20)
    exp_month = models.IntegerField(null=False, validators=[MinValueValidator(1), MaxValueValidator(12)])
    exp_year = models.IntegerField(null=False, validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    name_on_card = models.CharField(null=True, blank=True, max_length=255)

    def display_number(self):
        print(str(self.card_number)[-4:])
        return "XXXX XXXX XXXX " + str(self.card_number)[-4:]

   
class UserJWTtokens(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    expiredAt = models.DateTimeField()
    
class ResetPassword(models.Model):
    email = models.CharField(max_length=255)
    otp = models.CharField(max_length=255, blank=True, null=True)
    reset_password_token = models.CharField(max_length=255, unique=True)
    otp_expires_at = models.DateTimeField(default='2000-01-01 01:01:30.475275')

   
class UserProduct(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('product', 'user')
        
class WishlistedProduct(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')
    
class Review(models.Model):
  product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
  user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
  review = models.CharField(max_length=300)
  rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)
    
# @receiver(post_save, sender=User)
# def create_jwt_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         print(dir(Token))
#         Token.objects.create(user=instance)
#         print("In receiver after", created,instance)