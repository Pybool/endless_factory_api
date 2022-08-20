from rest_framework import serializers
from orders.models import Order, Cart, CartItem, LineItem
from product.models import Product, Tag, Attachment, Category, Variant, OptionValue, OptionType
from accounts.models import WishlistedProduct, User, Address, Review, CreditCard
class LineItemProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id', 'name']
class LineItemVariantSerializer(serializers.ModelSerializer):
  product = LineItemProductSerializer(many=False)
  class Meta:
    model = Variant
    fields = ['id', 'price', 'product']

class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = ['number', 'created_at', 'total', 'is_shipped', 'id', 'items_count', 'tracking_number']

class LineItemIndexSerializer(serializers.ModelSerializer):
  variant = LineItemVariantSerializer(many=False)
  order = OrderSerializer(many=False)
  class Meta:
    model = LineItem
    fields = ['order', 'variant', 'price', 'dispatched', 'id', 'display_variant', 'tracking_number', 'quantity', 'tracking_number', 'courier_agency']

class UserShowSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'email', 'phone_number', 'shipping_addresses_count', 'country', 'avatar', 'credit_cards_count', 'company_name', 'company_mailing_address', 'company_description', 'tax_id_number', 'entity_type', 'payment_acceptance_type', 'bank_info', 'contact_preferences', 'number_of_employees', 'year_founded', 'gross_annual_revenue']

class UserIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'name', 'avatar', 'email']

class ReviewSerializer(serializers.ModelSerializer):
  user = UserIndexSerializer(many=False)
  class Meta:
    model = Review
    fields=('id', 'rating', 'review', 'user', 'created_at', 'updated_at')

class AddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = Address
    fields = ['id', 'first_name', 'last_name', 'line_1', 'line_2', 'city', 'zipcode', 'state', 'country', 'is_shipping_address']

class RegistrationSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'phone_number', 'name', 'password', 'user_type', 'country']
    extra_kwargs = {
      'password': {'write_only': True}
    }
    
    def save(self):
      user = User(
        email = self.validated_data['email'],
      )
      password = self.validated_data['password']
      confirm_password = self.validated_data['password']
      if password != confirm_password:
        raise serializers.ValidationError({'password': 'Passwords must match'})
      user.set_password(password)
      user.save()
      return user

class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ['id', 'name', 'image', 'slug']

class TagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = ['id', 'name', 'slug']

class OptionTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionType
    fields = ('id', 'name')

class OptionValueSerializer(serializers.ModelSerializer):
  class Meta:
    model = OptionValue
    fields = ('id', 'value')

class FavoruriteProductSerializer(serializers.ModelSerializer):
  option_type = OptionTypeSerializer(many=False)
  category = CategorySerializer(many=False)

  class Meta:
    model = Product
    fields=('id', 'name', 'slug', 'images', 'option_type', 'category')

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

class VariantSerializer(serializers.ModelSerializer):
  option_value = OptionValueSerializer(many=False)

  class Meta:
    model = Variant
    fields=('id', 'price', 'option_value', 'stock')

class ProductSerializer(serializers.ModelSerializer):
  category = CategorySerializer(many=False)
  variants = VariantSerializer(many=True)
  reviews = ReviewSerializer(many=True)
  search_tags = TagSerializer(many=True)
  option_type = OptionTypeSerializer(many=False)
  class Meta:
    model = Product
    fields=('id', 'name', 'new_arrival', 'description', 'min_order_quantity', 'max_order_quantity', 'color', 'model_number', 'category', 'option_type', 'delivery_option', 'product_type', 'search_tags', 'slug', 'variants', 'images', 'reviews')

class ProductUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields=('id', 'name', 'description', 'min_order_quantity', 'max_order_quantity', 'model_number', 'category','option_type')

class VariantUpdateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id', 'stock', 'price', 'option_value', 'product')

class VariantIndexSerializer(serializers.ModelSerializer):
  class Meta:
    model = Variant
    fields=('id', 'price')

class ProductIndexSerializer(serializers.ModelSerializer):
  category = CategorySerializer(many=False)
  variants = VariantIndexSerializer(many=True)
  class Meta:
    model = Product
    fields = ['name', 'images', 'category', 'variants', 'slug']
  
class CartProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['name', 'images', 'slug']

class CartItemSerializer(serializers.ModelSerializer):
  product = CartProductSerializer(many=False)
  class Meta:
    model = CartItem
    fields = ['id', 'option_value', 'option_type', 'quantity', 'price', 'products', 'display_variant']

class CartSerializer(serializers.ModelSerializer):
  cart_items = CartItemSerializer(many=True)
  class Meta:
    model = Cart
    fields = ['token', 'cart_items', 'total', 'items_count']

class CreditCardSerializer(serializers.ModelSerializer):
  class Meta:
    model = CreditCard
    fields = ['card_number', 'exp_month', 'exp_year', 'brand', 'display_number', 'name_on_card']
