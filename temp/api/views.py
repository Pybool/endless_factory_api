from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
import random
from django.utils.crypto import get_random_string
from django.conf import settings
import stripe
from accounts.models import WishlistedProduct, Address, Review
from product.models import Product, Category, Variant, OptionType, OptionValue, Tag, Attachment
from accounts.models import User, CreditCard, UserProduct
from orders.models import Cart, CartItem, Order, LineItem
from application.serializers import RegistrationSerializer, WishlistedProductSerializer, AddressSerializer, ProductSerializer, CategorySerializer, ProductIndexSerializer, VariantSerializer, ProductUpdateSerializer, VariantUpdateSerializer, TagSerializer, UserShowSerializer, LineItemIndexSerializer, CartSerializer, CreditCardSerializer, OptionTypeSerializer, OptionValueSerializer, ReviewSerializer, AttachmentSerializer


@api_view(['GET'])
def categories(request):
    categories = Category.objects.all()
    serializer= CategorySerializer(categories, many=True)
    return Response({'categories': serializer.data})

@api_view(['GET'])
def option_values(request):
    option_values = OptionValue.objects.select_related('option_type').filter(option_type__name=request.GET['option_type'])
    serializer= OptionValueSerializer(option_values, many=True)
    return Response({'option_values': serializer.data})

@api_view(['GET'])
def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.product_set.filter(is_active=True, approved=True)
    category_serializer = CategorySerializer(category, many=False)
    products_serializer= ProductSerializer(products, many=True)
    return Response({'category': category_serializer.data, 'products':products_serializer.data})

@api_view(['GET'])
def products(request):
    products = Product.objects.filter(is_active=True, approved=True)
    serializer= ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def new_arrivals_products(request):
    products = Product.objects.filter(is_active=True, approved=True,new_arrival=True)
    serializer= ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    serializer= ProductSerializer(product, many=False)
    
    product_variant = Variant.objects.filter(product_id=product.id)

    has_bought_the_product = LineItem.objects.select_related('order').filter(order__user_id=request.GET['user_id'], variant__in=product_variant).count() > 0 if request.GET['user_id'] != None else False
    has_reviewed_the_product = Review.objects.filter(user_id=request.GET['user_id'], product_id=product.id).count() > 0 if request.GET['user_id'] != None else False

    return Response({'product':serializer.data, 'has_bought_the_product': has_bought_the_product, 'has_reviewed_the_product': has_reviewed_the_product})

@api_view(['GET'])
def product_form_data(request):
    categories = Category.objects.all()
    categories_serializer= CategorySerializer(categories, many=True)

    option_types = OptionType.objects.all()
    option_type_serializer = OptionTypeSerializer(option_types, many=True)

    tags = Tag.objects.all()
    tag_serializer = TagSerializer(tags, many=True)

    return Response({'categories': categories_serializer.data, 'option_types': option_type_serializer.data, 'tags': tag_serializer.data, 'status': 'ok'})


@api_view(['POST'])
def login(request):
    email = request.POST.get('email')
    user_type = request.POST.get('user_type')
    password = request.POST.get('password')
    user = authenticate(request, email=email, password=password) or User.objects.filter(email=email, password=password, user_type=user_type).first()
    data = {}
    if user is not None:
        data['status'] = 'ok'
        data['cart_token'] = user.cart_token
        data['user_id'] = user.id
        data['token'] = Token.objects.get(user=user).key
        return Response(data)
    else:
        data['status'] = 'error'
        data['error'] = 'Invalid login credentials'
        return Response(data, status=401)
    

@api_view(['POST'])
def signup(request):
    serializer = RegistrationSerializer(data = request.data)
    data = {}
    if serializer.is_valid():
        user = serializer.save()

        cart = Cart.objects.create(token=get_random_string(length=32))
        user.cart_token = cart.token
        user.save()

        data['status'] = 'ok'
        data['email'] = user.email
        data['cart_token'] = user.cart_token
        data['token'] = Token.objects.get(user=user).key
        return Response(data)
    else:
        data = serializer.errors
        return Response({'status': 'error', 'errors': data})
    

@api_view(['POST'])
@login_required
def mark_product_wishlisted(request):
    try:

        product = Product.objects.get(pk=request.POST['product'])
        data = {}
        WishlistedProduct.objects.get_or_create(product=product, user=request.user)
        data['response'] = 'Product added to Wishlist successfully'
        return Response(data)
    except:
        return Response({'status': 'error', 'message': 'Product not found'})

@api_view(['DELETE'])
@login_required
def mark_product_unwishlisted(request):
    try:
        product = Product.objects.get(pk=request.POST['product'])
        data = {}
        WishlistedProduct.objects.filter(product=product, user=request.user).delete()
        data['response'] = 'Product removed from wishlist successfully'
        return Response(data)
    except:
        return Response({'status': 'error', 'message': 'Product not found'})

@api_view(['GET', 'POST'])
@login_required
def user_profile(request):
    serializer= UserShowSerializer(request.user, many=False)
    if request.method == 'POST':
        serializer= UserShowSerializer(request.user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'user': serializer.data, "status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    return Response({'user': serializer.data, "status": 'ok'})

@api_view(['GET'])
# @login_required
def orders(request):
    status = request.GET.get('status')
    if status is not None:
        if status == 'delivered':
            order_items = LineItem.objects.select_related('order', 'variant').filter(order__user_id=request.user.id, dispatched=True)
            serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'order_items': serializer.data})
        elif status == 'processing':
            order_items = LineItem.objects.select_related('order', 'variant').filter(order__user_id=request.user.id, dispatched=False)
            serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'order_items': serializer.data})
    else:
        order_items = LineItem.objects.select_related('order', 'variant').filter(order__user_id=request.user.id)
        serializer= LineItemIndexSerializer(order_items, many=True)
        return Response({'order_items': serializer.data})

@api_view(['GET'])
@login_required
def seller_orders(request):
    status = request.GET.get('status')
    product_id = request.GET.get('product_id')
    if product_id != None:
        seller_product_variants = Variant.objects.filter(product__in=request.user.products())
    else:
        seller_product_variants = Variant.objects.filter(product_id=product_id)

    if status is not None:
        if status == 'delivered':
            order_items = LineItem.objects.select_related('variant').filter(dispatched=True, variant__in=seller_product_variants)
            serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'order_items': serializer.data})
        elif status == 'processing':
            order_items = LineItem.objects.select_related('variant').filter(dispatched=False, variant__in=seller_product_variants)
            serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'order_items': serializer.data})
    else:
        order_items = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
        serializer= LineItemIndexSerializer(order_items, many=True)
        return Response({'order_items': serializer.data})

@api_view(['GET', 'POST'])
@login_required
def seller_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer= ProductSerializer(product, many=False)
        if request.method == 'POST':
            serializer= ProductUpdateSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                product.search_tags.clear()
                tags = Tag.objects.filter(pk__in=request.POST.get('search_tags').split(','))
                for tag in tags:
                    product.search_tags.add(tag)
                return Response({'product': serializer.data, "status": 'ok'})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})
        return Response({'product': serializer.data, 'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Product'})

@api_view(['GET', 'POST'])
@login_required
def seller_products(request):
    seller_products = request.user.products()
    serializer= ProductSerializer(seller_products, many=True)
    if request.method == 'POST':
        product = Product()
        serializer= ProductUpdateSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            tags = Tag.objects.filter(pk__in=request.POST.get('search_tags').split(','))
            for tag in tags:
                product.search_tags.add(tag)
            user_product = UserProduct(user=request.user, product=serializer.instance)
            user_product.save()
            return Response({'id': product.id, "status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@login_required
def product_variants(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer= VariantSerializer(product.variant_set.all(), many=True)

        if request.method == 'POST':
            variant = Variant()

            serializer= VariantUpdateSerializer(variant, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": 'ok'})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})
        return Response({'variants': serializer.data, 'product_option_type': product.option_type.name, 'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Product'})

@api_view(['GET', 'POST'])
@login_required
def product_images(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer= AttachmentSerializer(product.attachment_set.all(), many=True)
        if request.method == 'POST':
            image = Attachment(product_id=request.POST.get('product_id'))
            image.file = request.FILES.get('file')
            image.attachment_type = 'Image'
            image.save()
            return Response({"status": 'ok'})
        return Response({'images': serializer.data, 'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Something Went Wrong'})

@api_view(['DELETE'])
@login_required
def delete_product_image(request, pk):
    try:
        image = Attachment.objects.get(pk=pk)
        image.delete()
        return Response({"status": 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Image'})

@api_view(['GET', 'POST'])
@login_required
def product_reviews(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer= ReviewSerializer(product.review_set.all(), many=True)
        return Response({'reviews': serializer.data, 'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Product'})

@api_view(['POST'])
@login_required
def update_variant(request, pk):
    try:
        variant = Variant.objects.get(pk=pk)
        serializer= VariantUpdateSerializer(variant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Variant'})

@api_view(['GET'])
@login_required
def home_data(request):
    categories = Category.objects.all()
    categories_serializer= CategorySerializer(categories, many=True)

    most_searched_products = Product.objects.all()[:4]
    most_searched_products_serializer = ProductIndexSerializer(most_searched_products, many=True)

    best_products = Product.objects.all()[:4]
    best_products_serializer = ProductIndexSerializer(best_products, many=True)
    return Response({'categories': categories_serializer.data, 'most_searched_products': most_searched_products_serializer.data, 'best_products': best_products_serializer.data})

@api_view(['GET'])
@login_required
def seller_home_data(request):
    user_products = request.user.products()
    product_serializer = ProductIndexSerializer(user_products, many=True)
    seller_product_variants = Variant.objects.filter(product__in=user_products)

    orders = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
    order_serializer= LineItemIndexSerializer(orders, many=True)
    
    return Response({'orders': order_serializer.data, 'products': product_serializer.data})


@api_view(['GET', 'POST'])
@login_required
def addresses(request):
    addresses = request.user.addresses.all() #Should be a list of Objects
    serializer= AddressSerializer(addresses, many=True)
    if request.method == 'POST':
        address = Address()
        serializer= AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            request.user.addresses.add(address)
            return Response({'address': serializer.data, "status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    return Response({'addresses': serializer.data})

@api_view(['GET', 'POST'])
@login_required
def credit_cards(request):
    credit_cards = request.user.credit_cards.all()
  
    serializer= CreditCardSerializer(credit_cards, many=True)
    if request.method == 'POST':
        credit_card = CreditCard()
        serializer= CreditCardSerializer(credit_card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            request.user.credit_cards.add(credit_card)
            return Response({'credit_card': serializer.data, "status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    return Response({'credit_cards': serializer.data})

@api_view(['GET', 'POST'])
@login_required
def credit_card(request, pk):
    credit_card = request.user.credit_cards.filter(pk=pk).first()

    serializer= CreditCardSerializer(credit_card, many=False)
    # if request.method == 'POST':
    #     address = Address()
    #     serializer= AddressSerializer(address, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         request.user.addresses.add(address)
    #         return Response({'address': serializer.data, "status": 'ok'})
    #     else:
    #         return Response({'errors': serializer.errors, "status": 'error'})
    return Response({'credit_card': serializer.data})

@api_view(['GET', 'POST'])
@login_required
def wishlistedproducts(request):
    wishlisted_products = request.user.wishlistedproduct_set.all()
    serializer= WishlistedProductSerializer(wishlisted_products, many=True)
    return Response({'wishlisted_products': serializer.data})

@api_view(['GET'])
@login_required
def preferred_address(request):
    address = request.user.addresses.filter(is_shipping_address=True).first()
    serializer= AddressSerializer(address, many=False)
    return Response({'preferred_address': serializer.data, "status": 'ok'})

@api_view(['GET', 'PUT'])
@login_required
def address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    serializer= AddressSerializer(address, many=False)
    
    if request.method == 'PUT':
        serializer= AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'address': serializer.data, "status": 'ok'})
        else:
            return Response({'errors': serializer.errors, "status": 'error'})
    return Response({'address': serializer.data, "status": 'ok'})

@api_view(['POST'])
def request_otp(request):
    try:
        user = User.objects.get(email=request.POST.get('email'))
        # user.otp = random.randint(100000, 999999)
        user.otp = 123456
        user.reset_password_token = get_random_string(length=32)
        user.save()
        return Response({'otp': user.otp, 'reset_password_token': user.reset_password_token, 'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid Email'})

@api_view(['POST'])
def validate_otp(request):
    try:
        user = User.objects.get(reset_password_token=request.POST.get('reset_password_token'))
        is_otp_valid = user.otp == int(request.POST.get('otp'))
        return Response({'status':  "ok" if is_otp_valid else "error", 'reset_password_token': user.reset_password_token, 'message': "OTP validated" if is_otp_valid else "Inavlid OTP"})
    except:
        return Response({'status': 'error', 'message': 'Invalid reset password token'})

@api_view(['POST'])
def reset_password(request):
    try:
        user = User.objects.get(reset_password_token=request.POST.get('reset_password_token'))
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        if password == password_confirmation:
            user.password = password
            user.otp = None
            user.reset_password_token = None
            user.save()
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'error', 'message': 'Passwords should match'})
    except:
        return Response({'status': 'error', 'message': 'Invalid reset password token'})

@api_view(['POST'])
@login_required
def change_password(request):
    try:
        user = User.objects.get(email=request.POST.get('email'), password=request.POST.get('current_password'))
    
        user.password = request.POST.get('new_password')
        user.save()
        return Response({'status': 'ok'})
    except:
        return Response({'status': 'error', 'message': 'Invalid current password'})

@api_view(['GET'])
def cart(request):
    cart = get_cart(request)
    
    serializer = CartSerializer(cart, many=False)
    return Response({'cart': serializer.data, "status": 'ok'})

@api_view(['POST'])
def add_item_to_cart(request):
    cart = get_cart(request)
    variant = Variant.objects.get(pk=request.POST['variant'])
    cart_item = CartItem.objects.filter(cart=cart, variant=variant).first()
    if cart_item is not None:
        cart_item.quantity +=int(request.POST['quantity'])

        if cart_item.quantity > variant.stock:
            return Response({'error': 'Insufficient stock', "status": 'error'})
        
        cart_item.price = int(cart_item.quantity) * variant.price
        cart_item.save()
        return Response({'message': 'Item added to cart successfully.', "status": 'ok'})
    else:
        cart_item = CartItem.objects.create(cart=cart, variant=variant, option_type=variant.product.option_type.name, option_value=variant.option_value.value)
        
        if cart_item.quantity > variant.stock:
            return Response({'error': 'Insufficient stock', "status": 'error'})
        
        cart_item.price = int(cart_item.quantity) * variant.price
        cart_item.save()
        return Response({'message': 'Item added to cart successfully.', "status": 'ok'})

@api_view(['POST'])
def update_cart_item(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    cart_item.quantity = int(request.POST['quantity'])

    if cart_item.quantity > cart_item.variant.stock:
        return Response({'error': 'Insufficient stock', "status": 'error'})
    else:
        cart_item.price = int(cart_item.quantity) * cart_item.variant.price
        cart_item.save()
        return Response({'message': 'Cart item updated successfully.', "status": 'ok'})


@api_view(['DELETE'])
def remove_item_from_cart(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    cart_item.delete()
    return Response({'message': 'Cart item removed successfully.', "status": 'ok'})

@api_view(['POST'])
@login_required
def reviews(request):
    product = Product.objects.filter(pk=request.POST['product_id']).first()
    review = Review(product=product, user=request.user, rating=int(request.POST['rating']), review=request.POST['review'])
    review.save()
    return Response({'message': 'Your review has been submitted successfully.', 'status': 'ok'})

@api_view(['POST'])
@login_required
def checkout(request):
    cart = get_cart(request)
    stripe_pub_key = settings.STRIPE_PUBLISHABLE_KEY
    
    if request.method == 'POST':
        try:
            stripe_order_token = request.POST['stripe_token']
            charge = stripe.Charge.create(
                amount = int(100*cart.grand_total()),
                currency='usd',
                description='Order payment',
                source = stripe_order_token
            )
            
            if charge['status'] == 'succeeded':
                order = Order(user=request.user)
                order.item_total = cart.total()
                order.total = cart.grand_total()
                order.endless_factory_cut = cart.endless_factory_cut()
                order.shipping_address = Address.objects.filter(pk=request.POST['address_id']).first()
                order.save()
                order.set_line_items_from_cart(cart)
                order.set_transaction(request.user, charge, request.POST['card_number'], request.POST['save_card'])
                cart.reset()
                return Response({'message': 'Your order has been placed successfully.', 'status': 'ok', 'order_id': order.number})
            else:
                return Response({'message':'Your card was declined.', 'status': 'error'})
        except:
            return Response({'message':'Your card was declined.', 'status': 'error'})

# Private methods =========================
def get_cart(request):
    token = request.GET.get('cart_token') or request.POST.get('cart_token')
    user_cart, created = Cart.objects.get_or_create(token=token)
    return user_cart
