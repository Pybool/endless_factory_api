from decimal import Decimal
import uuid
from rest_framework import serializers
from chat.models import DocumentChatAttachment, ImageChatAttachment, Message, VideoChatAttachment
from dashboard.models import Refunds
from marketing.models import Campaign
from orders.models import Order, Cart, CartItem, LineItem, Transaction
from products.models import Product, Tag, Attachment, Category, Variant, OptionValue, OptionType
from accounts.models import IDCardsAttachment, ProofBusinessAttachment, WishlistedProduct, User, Address, Review, CreditCard
import operator, functools
from django.db import transaction

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
    fields = ['id', 'subtitle']
    
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
    fields = ['user', 'first_name', 'last_name', 'line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address']

class GetAddressSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Address
    fields = ['id','user', 'first_name', 'last_name', 'line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address']

class OrderSerializer(serializers.ModelSerializer):
  shipping_address = OrderAddressSerializer(many=False)
  class Meta:
    model = Order
    fields = ['number', 'created_at', 'total','shipping_address', 'is_shipped', 'id', 'items_count', 'tracking_number']

class LineItemIndexSerializerDashboard(serializers.ModelSerializer):
  variant = LineItemVariantSerializer(many=False)
  order = OrderSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['order', 'variant', 'price','cost_price', 'dispatched', 'id', 'display_variant', 'tracking_number', 'quantity', 'tracking_number', 'courier_agency','order_status']


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
    fields = ['id', 'name', 'image', 'slug']

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
    fields=('id', 'price', 'option_value', 'stock')

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
    
class VariantSerializer(serializers.ModelSerializer):
  option_value = OptionValueSerializer(many=False)

  class Meta:
    model = Variant
    fields=('id', 'price', 'option_value', 'stock')
    
class CreateVariantSerializer(serializers.ModelSerializer):
  # option_value = OptionValueSerializer(many=False)

  class Meta:
    model = Variant
    fields=('option_value', 'stock', 'price','product')
    

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
    fields = ('category','option_type','title','subtitle', 'description','condition_option','business_source', 'model_number','account_manager_phone_1','company_mailing_address','company_address_1', 'search_tags','eco_friendly','duration','price','cost_price','initial_stock')

class ProductUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields=('id', 'subtitle', 'description', 'min_order_quantity', 'max_order_quantity', 'model_number', 'category','option_type')

class VariantUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id', 'stock', 'price','cost_price', 'option_value', 'product')

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
    fields = ['token', 'cart_items', 'total', 'items_count']

class LineItemIndexSerializer(serializers.ModelSerializer):
  user = OrderUserSerializer(many=False)
  variant = LineItemVariantSerializer(many=False)
  order = OrderSerializer(many=False)
  product = ProductSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['user','order', 'variant','product', 'price','cost_price', 'dispatched', 'id', 'display_variant', 'tracking_number', 'quantity', 'tracking_number', 'courier_agency']

class CreditCardSerializer(serializers.ModelSerializer):
  class Meta:
    model = CreditCard
    fields = ['id','user','card_number', 'exp_month', 'exp_year', 'brand', 'display_number', 'name_on_card']

class CampaignUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'phone_number', 'name', 'user_type', 'country']

class PromoSerializer(serializers.ModelSerializer):
  listings = ProductSerializer(many=True)
  variants = VariantSerializer(many=True)
  class Meta:
    model = Campaign
    fields = ['campaign_name','is_active', 'start_date', 'end_date','listings','variants']



class CampaignSerializer(serializers.ModelSerializer):

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
    fields = ['campaign_name','user', 'start_date', 'end_date', 'sold_id', 'ad_fees','price_range','currency','paid']


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
    sender = CampaignUserSerializer(many=False)
    receiver = CampaignUserSerializer(many=False)
    
    class Meta:
        model = Message
        fields = ['id','chat_uid','sender', 'receiver', 'message','attached_media_type', 'timestamp']
  
class MessageSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    sender = serializers.SlugRelatedField(many=False, slug_field='id', queryset=User.objects.all()) # Change Id to email
    receiver = serializers.SlugRelatedField(many=False, slug_field='id', queryset=User.objects.all())
    
    def create(self,validated_data):
    
      with transaction.atomic():
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        chat_uid = validated_data['chat_uid']
        print(chat_uid,type(chat_uid))
        if chat_uid == "None":
           validated_data['chat_uid'] = str('c-uid') + str(uuid.uuid4()) + "@" + str(sender) + "_" + str(receiver)
           print(validated_data['chat_uid'])
        else:
            conversation_id = Message.objects.filter(chat_uid=str(validated_data['chat_uid']))
            print("Conversation id ", conversation_id)
        validated_data['sender'] = User.objects.get(pk=int(validated_data['sender']))
        validated_data['receiver'] = User.objects.get(pk=int(validated_data['receiver']))
        print(validated_data)
        instance = self.Meta.model(**validated_data)
        instance.save()
       
        return instance
      
    class Meta:
        model = Message
        fields = ['id','sender', 'receiver', 'message', 'timestamp']

class MessageAttachmentSerializer(serializers.ModelSerializer):

  def create(self, validated_data):
    
        documents = self.context['documents']
        media_type = str(documents).rsplit(" ",1)[1]
        message = Message.objects.get(pk=int(validated_data['message']))
        
        for document in documents:
            if 'document' in media_type:
              MessageAttachmentSerializer.Meta.model = DocumentChatAttachment # Update model in Meta class to documents chat attachment model
              instance = DocumentChatAttachment.objects.create(message=message,file=document,attachment_type="Document")
            elif 'image' in media_type:
              MessageAttachmentSerializer.Meta.model = ImageChatAttachment # Update model in Meta class to image chat attachment model
              instance = ImageChatAttachment.objects.create(message=message,file=document,attachment_type="Image")
            elif 'video' in media_type:
              MessageAttachmentSerializer.Meta.model = VideoChatAttachment # Update model in Meta class to video chat attachment model
              instance = VideoChatAttachment.objects.create(message=message,file=document,attachment_type="Video")
            # instance.save()
        print(MessageAttachmentSerializer.Meta.model)
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