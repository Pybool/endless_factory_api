from datetime import date, datetime
from decimal import Decimal
import uuid
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from careers.models import Applicant, ApplicantsResume, Applications, Company, Job
from chat.models import Conversation, DocumentChatAttachment, ImageChatAttachment, Message, Room, VideoChatAttachment
from dashboard.models import Refunds
from helpers import convert_to_timezone, get_user_timezone
from marketing.models import Campaign
from notifications.models import Notifications
from order_tracking.models import OrderTracking
from orders.models import Order, Cart, CartItem, LineItem, Transaction
from products.models import Product, Tag, Attachment, Category, Variant, OptionValue, OptionType
from accounts.models import IDCardsAttachment, NDAAttachment, NDAPurchases, NDAUser, ProofBusinessAttachment, QuotesAttachment, WishlistedProduct, User, Address, Review, CreditCard ,NDA,NDAProposals
from accounts.chatuser_serializer import UserSerializer as ChatUserSerializer_
import operator, functools
from django.db import transaction
import logging
log = logging.getLogger(__name__)

class TransactionsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transaction
    fields = '__all__'
    
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'phone_number', 'name', 'password', 'user_type', 'country']

class SellerCentreBasicInfoSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['store_name', 'entity_type', 'account_manager_name', 'account_manager_phone_1', 'account_manager_phone_2']
    
    
class SellerCentreBusinessInfoSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['store_name', 'entity_type', 'account_manager_name', 'account_manager_phone_1', 
              'account_manager_phone_2',
              'referrer_email', 'has_existing_shop', 'account_manager_name', 'company_name', 
              'company_address_1', 'company_address_2','company_postal_code','city_location',
              'company_ceo_name'
              ]
    
class LineItemProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields=('id', 'title','subtitle', 'description','price', 'color', 'business_source','account_manager_phone_1','company_mailing_address','company_address_1', 'category', 'option_type', 'delivery_option', 'product_type', 'search_tags', 'slug', 'images', 'reviews')

    
    
class LineItemVariantSerializer(serializers.ModelSerializer):
  product = LineItemProductSerializer(many=False)
  class Meta:
    model = Variant
    fields = ['id', 'price', 'product']

class OrderUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id','email', 'phone_number', 'name', 'user_type', 'country']

class OrderAddressSerializer(serializers.ModelSerializer):
  # addresses = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
  class Meta:
    model = Address
    fields = ['user','line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address']

class AddressSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Address
    fields = ['user', 'first_name', 'last_name', 'line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address','is_default_address']

class GetAddressSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Address
    fields = ['id','user', 'first_name', 'last_name', 'line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address','is_default_address']

class OrderSerializer(serializers.ModelSerializer):
  shipping_address = OrderAddressSerializer(many=False)
  class Meta:
    model = Order
    fields = ['number', 'created_at', 'total','shipping_address', 'is_shipped', 'id', 'items_count', 'tracking_number']

class LineItemPriceIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = LineItem
    fields = ['price']


class UserAllSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id','email', 'name', 'user_type', 'password', 'company_name', 'country', 'company_mailing_address', 'company_description', 'tax_id_number', 'phone_number', 'entity_type', 'payment_acceptance_type', 'bank_info', 'contact_preferences', 'number_of_employees', 'year_founded', 'gross_annual_revenue']


class UserShowSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'email', 'phone_number', 'shipping_addresses', 'country', 'avatar', 'company_name', 'company_mailing_address', 'company_description', 'tax_id_number', 'entity_type', 'payment_acceptance_type', 'bank_info', 'contact_preferences', 'number_of_employees', 'year_founded', 'gross_annual_revenue']

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['name','phone_number', 'email', 'shipping_addresses', 'country', 'company_name', 'company_mailing_address', 'company_description', 'tax_id_number', 'entity_type', 'bank_info','number_of_employees', 'year_founded', 'gross_annual_revenue']


class UserIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'avatar', 'email']

class ReviewSerializer(serializers.ModelSerializer):
  user = UserIndexSerializer(many=False)
  class Meta:
    model = Review
    fields=('id', 'rating', 'review', 'user', 'created_at', 'updated_at')


    # depth = 1
    
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'phone_number', 'name', 'password', 'user_type', 'country']
    extra_kwargs = {
      'password': {'write_only': True}
    }
  
  def create(self,validated_data):
       password = validated_data.pop('password',None)
       instance = self.Meta.model(**validated_data)
       if password is not None:
           instance.set_password(password)
       instance.save()
       return instance
  
class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ['id', 'name', 'image', 'slug','parent']

class NewCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ['name','description']
    
class TagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = ['id', 'name', 'slug']

class OptionTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionType
    fields = ('id', 'name')

class NewOptionTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionType
    fields = ['name']
    
class OptionValueSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionValue
    fields = ('id', 'value','option_type')

class NewOptionValueSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionValue
    fields = ('value','option_type')


class FavoruriteProductSerializer(serializers.ModelSerializer):
  option_type = OptionTypeSerializer(many=False)
  category = CategorySerializer(many=False)

  class Meta:
    model = Product
    fields=('id', 'subtitle', 'slug', 'images', 'option_type', 'category')

class WishlistedProductVariantSerializer(serializers.ModelSerializer):
  option_value = OptionValueSerializer(many=False)
  class Meta:
    model = Variant
    fields=('id', 'price', 'option_value','initial_stock', 'stock')

class WishlistedProductSerializer(serializers.ModelSerializer):
  product =FavoruriteProductSerializer(many=False)

  class Meta:
    model = WishlistedProduct
    fields = ('product',)



class AttachmentSerializer(serializers.ModelSerializer):

  class Meta:
    model = Attachment  
    fields=('id', 'url', 'attachment_type')
    
class NewAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        documents = self.context['documents']
        product = Product.objects.get(pk=int(validated_data['product'].id))
        for document in documents:
            instance = Attachment.objects.create(product=product,file=document,attachment_type="Image")
            instance.save()
        return product
      
  class Meta:
    model = Attachment  
    fields=('product', 'file', 'attachment_type')

class IdCardAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        print(validated_data)
        documents = self.context['id-documents']
        user = User.objects.get(pk=int(validated_data['user']))
        for document in documents:
            instance = IDCardsAttachment.objects.create(company=user,file=document,attachment_type="Image")
            instance.save()
        return user
      
  class Meta:
    model = Attachment  
    fields=('product', 'file', 'attachment_type')
    
class ProofBusinessAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        documents = self.context['pbo-documents']
        user = User.objects.get(pk=int(validated_data['user']))
        for document in documents:
            instance = ProofBusinessAttachment.objects.create(company=user,file=document,attachment_type="Image")
            instance.save()
        return user
      
  class Meta:
    model = Attachment  
    fields=('product', 'file', 'attachment_type')
    
class QuoteAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
        documents = self.context['quote-documents']
        quote = validated_data['quote']
        print("Type ",str(documents).rsplit(" ",1)[1])
        attachment_type = "Image" if "image" in str(documents).rsplit(" ",1)[1] else "Document"
          
        for document in documents:
            instance = QuotesAttachment.objects.create(quote=quote,file=document,attachment_type=attachment_type)
            instance.save()
        return instance
      
  class Meta:
    model = Attachment  
    fields=('product', 'file', 'attachment_type')
    
class VariantSerializer(serializers.ModelSerializer):
  option_value = OptionValueSerializer(many=False)

  class Meta:
    model = Variant
    fields=('id','product', 'price', 'option_value','initial_stock', 'stock') #,'variant_images'
    
class CreateVariantSerializer(serializers.ModelSerializer):
  # option_value = OptionValueSerializer(many=False)

  class Meta:
    model = Variant
    fields=('option_value','initial_stock', 'stock', 'price','product')
    

class ProductSerializer(serializers.ModelSerializer):
  category = CategorySerializer(many=False)
  variants = VariantSerializer(many=True)
  reviews = ReviewSerializer(many=True)
  search_tags = TagSerializer(many=True)
  option_type = OptionTypeSerializer(many=False)
  class Meta:
    model = Product
    fields=('id', 'title','subtitle', 'description','price','cost_price','initial_stock','current_stock', 'min_order_quantity', 'max_order_quantity', 'color', 'business_source','account_manager_phone_1','company_mailing_address','company_address_1', 'category', 'option_type', 'delivery_option', 'product_type', 'search_tags', 'slug', 'variants', 'images', 'reviews')
  
    
class NewProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ('category','option_type','title','subtitle', 'description','condition_option','business_source', 'model_number','account_manager_phone_1','company_mailing_address','company_address_1', 'search_tags','eco_friendly','duration','price','cost_price','initial_stock','current_stock','min_order_quantity','max_order_quantity')

class ProductUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields=('id', 'subtitle', 'description', 'min_order_quantity', 'max_order_quantity', 'model_number', 'category','option_type')

class VariantUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id','initial_stock', 'stock', 'price', 'option_value', 'product')

class VariantIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id', 'price')

class ProductIndexSerializer(serializers.ModelSerializer):
  category = CategorySerializer(many=False)
  variants = VariantIndexSerializer(many=True)
  class Meta:
    model = Product
    fields = ['title','subtitle', 'images', 'category', 'model_number', 'variants', 'slug']

######################################################################################################
class SellerListingVariantIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id', 'price')

class ProductIndexSerializer(serializers.ModelSerializer):
  category = CategorySerializer(many=False)
  variants = SellerListingVariantIndexSerializer(many=True)
  class Meta:
    model = Product
    fields = ['title','subtitle', 'images', 'category', 'model_number', 'variants', 'slug']
    
#########################################################################################################
class CartProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['subtitle', 'images', 'slug']

class CartItemSerializer(serializers.ModelSerializer):
  products = CartProductSerializer(many=False)
  class Meta:
    model = CartItem
    fields = ['id', 'option_value', 'option_type', 'quantity', 'price','cost_price', 'products', 'display_variant']

class CartSerializer(serializers.ModelSerializer):
  cart_items = CartItemSerializer(many=True)
  class Meta:
    model = Cart
    fields = ['id','token', 'cart_items', 'total', 'items_count']

class OrderTrackingSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderTracking
    fields = '__all__'

class OrderTrackingLineItemSerializer(serializers.ModelSerializer):
  ordertracking = OrderTrackingSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['order_number','tracking_number','order_status', 'business_source', 'order_status_desc', 'expected_delivery_timeframe','created_at','updated_at']



class LineItemIndexSerializer(serializers.ModelSerializer):
  user = OrderUserSerializer(many=False)
  variant = LineItemVariantSerializer(many=False)
  order = OrderSerializer(many=False)
  product = ProductSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['user','order', 'variant','product', 'price','cost_price', 'id', 'display_variant', 'tracking_number', 'quantity', 'tracking_number', 'courier_agency','order_status','expected_delivery_timeframe']


class ChatUsersProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id']
    
class ChatUsersVariantIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('product')
  

class LineItemChatIndexSerializer(serializers.ModelSerializer):
  variant = ChatUsersVariantIndexSerializer(many=False)
  product = ChatUsersProductSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['variant','product']


class CreditCardSerializer(serializers.ModelSerializer):
  class Meta:
    model = CreditCard
    fields = ['id','user','card_number', 'exp_month', 'exp_year', 'brand', 'display_number', 'name_on_card']



class LineItemIndexSerializerDashboard(serializers.ModelSerializer):
  variant = LineItemVariantSerializer(many=False)
  order = OrderSerializer(many=False)
  product = ProductSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['order','product', 'variant', 'price','cost_price', 'id', 'display_variant', 'tracking_number', 'quantity', 'order_number', 'courier_agency','order_status']


class CampaignUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'phone_number', 'name', 'user_type', 'country']

class AdsSerializer(serializers.ModelSerializer):
  listings = ProductSerializer(many=True)
  variants = VariantSerializer(many=True)
  class Meta:
    model = Campaign
    fields = ['id','campaign_name','sold_id','ad_fees','sales','is_active','is_schedule', 'start_date', 'end_date','listings','variants']


class CampaignSerializer(serializers.ModelSerializer):
  
  def is_sheduled(self,start,end,tz=''):
    log.info(tz)
    tznow = get_user_timezone(tz)
    log.info(f"dcvc {tznow , convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz)} and {tznow , convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)}")
    log.info(f"dcvc {tznow >= convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz)} and {tznow <= convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)}")
    return tznow >= convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz) and tznow <= convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)
       
    
  def parseListings(self,data):
    
    keys_tuple = []
    listings_keys = ["product_id","variants"]
    
    for key in listings_keys:
      get_value = operator.itemgetter(key)
      list_of_values = functools.partial(map, get_value)
      list_of_values = list(list_of_values(data))
      keys_tuple.append(list_of_values)
    print(keys_tuple[0] , keys_tuple[1])
    return keys_tuple[0] , keys_tuple[1]
    
  def get_listings_Object(self,data):
    
        count = 0
        listings_lst = []
        variants_lst = []
        listings_variant_lst = []
        discount = 15 or data['discount']
        percent_discount = discount/100
        listings_obj,variants_obj = self.parseListings(data['listings'])
        assert len(listings_obj) == len(variants_obj)
        for variants in variants_obj:
          with transaction.atomic():
            if len(variants) == 0: #No product variant selected for product
                  instance = Product.objects.get(pk=int(listings_obj[count]))
                  listings_lst.append(instance)
                  # instance.price = Decimal(float(instance.price) - (float(instance.price) * (percent_discount)))
                  instance.discount = Decimal(percent_discount)
                  instance.save()
                  
            elif len(variants) >= 1: #Update Product Variants in database if a variant was specified
              for variant in variants:
                instance = Variant.objects.get(pk=int(variant))
                assert instance.product_id == listings_obj[count]
                # instance.price = Decimal(float(instance.price) - (float(instance.price) * (percent_discount)))
                instance.discount = Decimal(percent_discount)
                instance.save()
                product_instance = Product.objects.get(pk=int(instance.product_id))
                variants_lst.append(instance)
                listings_variant_lst.append(product_instance)
          count+=1
        print( listings_lst , variants_lst, listings_variant_lst)
        return listings_lst , variants_lst, listings_variant_lst
  
  def create(self,validated_data):
    
      with transaction.atomic():
        user = User.objects.get(pk=int(validated_data['user']))
        validated_data['user'] = user
        validated_data['is_schedule'] = self.is_sheduled(validated_data['start_date'],validated_data['end_date'],validated_data['tz'])
        log.info(validated_data['is_schedule'])
        listings = validated_data['listings']
        variants = validated_data['variants']
        listings_variants = validated_data['listings_variants']
        all_products = [*listings, *listings_variants]
        validated_data.pop('listings',None)
        validated_data.pop('variants',None)
        validated_data.pop('listings_variants',None)
        instance = self.Meta.model(**validated_data)
        instance.save()
        instance.listings.set(all_products)
        instance.variants.set(variants)
        return instance
  
  class Meta:
    model = Campaign
    fields = ['campaign_name','user', 'start_date', 'end_date','is_schedule', 'sold_id', 'ad_fees','price_range','currency','paid','tz']


#############Chat Serializers################
#User Serializer

# Message Serializer
class ChatUserSerializer(serializers.ModelSerializer):
    """For Serializing User"""
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'name', 'user_type', 'country']

# Message Serializer

class MessageDownloadSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    from_user = CampaignUserSerializer(many=False)
    to_user = CampaignUserSerializer(many=False)
    
    class Meta:
        model = Message
        fields = ['id','conversation','from_user', 'to_user', 'content','attached_media_type', 'timestamp']
  
class MessageSerializer(serializers.ModelSerializer):
    """For Serializing Message"""

    class Meta:
        model = Message
        fields = ['id','conversation','from_user', 'to_user','content','event']

class MessageAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
    
        documents = self.context['documents']
        message = Message.objects.get(id=validated_data['message'])
        try:
          media_type = validated_data['attached_media_type']#str(documents).rsplit(" ",1)[1]
          
          for document in documents:
              if 'document' in media_type:
                MessageAttachmentSerializer.Meta.model = DocumentChatAttachment # Update model in Meta class to documents chat attachment model
                instance = DocumentChatAttachment.objects.create(message=message,file=document,attachment_type="document")
              elif 'image' in media_type:
                MessageAttachmentSerializer.Meta.model = ImageChatAttachment # Update model in Meta class to image chat attachment model
                instance = ImageChatAttachment.objects.create(message=message,file=document,attachment_type="image")
              elif 'video' in media_type:
                MessageAttachmentSerializer.Meta.model = VideoChatAttachment # Update model in Meta class to video chat attachment model
                instance = VideoChatAttachment.objects.create(message=message,file=document,attachment_type="video")
              # instance.save()
          print(MessageAttachmentSerializer.Meta.model)
        except Exception as e:
          return 1 or message
        return 1 or message
      
  class Meta:
    
    model = ImageChatAttachment # Make default model Image (This model is transient cos it if dynamically changed by the if conditions above)
    fields=('message', 'file', 'attachment_type')


class NewRefundSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Refunds
        fields = ['customer', 'refund_id', 'amount', 'currency', 'related_charge', 'refund_reason', 'status']     

class RefundSerializer(serializers.ModelSerializer):
  
    class Meta:
          model = Refunds
          fields = ['id', 'customer', 'refund_id', 'amount', 'related_charge', 'refund_reason', 'status', 'created_at','updated_at']
          
class InboxSerializer(serializers.ModelSerializer):
  
    item = LineItemIndexSerializer(many=False)
    class Meta:
      model = Notifications
      fields=('tracking_number', 'user','item', 'message','subject', 'created_at')

class CareerUserSerilaizer(serializers.ModelSerializer):

  class Meta:
      model = User
      fields= ("company_name","user_type")
      
class CareerCompanyUserSerilaizer(serializers.ModelSerializer):
  user = CareerUserSerilaizer(many=False)
  class Meta:
      model = Company
      fields= "__all__"

class JobSerializer(serializers.ModelSerializer):
    company = CareerCompanyUserSerilaizer(many=False)
    class Meta:
      model = Job
      fields= "__all__"
      
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
      model = Applications
      fields= ("company","job","applicant")

class ApplicationResumeSerializer(serializers.ModelSerializer):
    
      def create(self, validated_data):
        documents = self.context['resume-documents']
        application = Applications.objects.get(job=get_object_or_404(Job,slug=validated_data['slug']), applicant= get_object_or_404(Applicant,user=validated_data['user']))
        for document in documents:
            instance = ApplicantsResume.objects.create(application=application,file=document,attachment_type="pdf")
            instance.save()
        return application
      
      class Meta:
        model = ApplicantsResume  
        fields=('application', 'file', 'attachment_type')

class NDAUserSerializer(serializers.ModelSerializer):
    class Meta:
      model = NDAUser
      fields= ("user",)
      
class NDAProposalsSerializer(serializers.ModelSerializer):
    to_user = serializers.SerializerMethodField()
    from_user = serializers.SerializerMethodField()
    
    def get_from_user(self, obj):
        return get_object_or_404(User,id=NDAUserSerializer(obj.from_user).data['user']).name

    def get_to_user(self, obj):
        return get_object_or_404(User,id=NDAUserSerializer(obj.to_user).data['user']).name
      
    class Meta:
      model = NDAProposals
      fields= "__all__"

class NDAAttachmentSerializer(serializers.ModelSerializer):
  
    def create(self):
        documents = self.context['nda-document']
        
        attachment_type = "document"
        for document in documents:
            instance = NDAAttachment.objects.create(file=document,attachment_type=attachment_type)
            instance.save()
        return instance
      
    class Meta:
      model = NDAAttachment
      fields= "__all__"


class NDASerializer(serializers.ModelSerializer):
    
    class Meta:
      model = NDA
      fields= "__all__"
      
class NDAPurchaseSerializer(serializers.ModelSerializer):
    
    class Meta:
      model = NDAPurchases
      fields= "__all__"
      