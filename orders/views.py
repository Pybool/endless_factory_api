import logging
log = logging.getLogger(__name__)
from uuid import uuid4
import uuid, time
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from accounts.authentication import JWTAuthenticationMiddleWare, decode_access_token, get_authorization_token
from rest_framework.response import Response
from accounts.models import Address, User, WishlistedProduct
from dashboard.transactions import InitiateTransaction
from endless_factory_api.serializers import CartSerializer, CategorySerializer, LineItemIndexSerializer, ProductIndexSerializer
from orders.utils import get_currrent_date_time
from products.models import Product, Variant, Category, Tag
from orders.models import Order, LineItem, Cart, CartItem
from rest_framework.views import APIView
import stripe
from django.views.decorators.csrf import csrf_exempt
from .utils import get_sample_response

# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt

# @method_decorator(csrf_exempt, name='dispatch')

class TestLogger(APIView):
    
    def get(self,request):
        log.info("Hey there it works!!")
        return Response({'message':'Logger worked', "status": True})

class CartView(APIView):
    
    def get(self,request,cart_token):
        cart = get_cart(request,cart_token)
        log.info("Cart ===> "+ str(cart))
        cart_serializer = CartSerializer(cart)
        log.warning('cart items retrieved')
        return Response({ 'lang': get_user_locale(request), 'cart':cart_serializer.data,'message':'Cart items retrieved successfully', "status": True})

    def put(self, request, pk):
        cart = get_cart(request,None)
        cart_item = CartItem.objects.get(pk=pk)
        cart_item.quantity = int(request.data['quantity'])

        if cart_item.quantity > cart_item.variant.stock:
           return Response({'message':'Insufficient stock!', "status": True})
        else:
            cart_item.price = int(cart_item.quantity) * cart_item.variant.price
            cart_item.save()
            return Response({'message':'Cart item updated successfully.', "status": True})

class AddCartView(APIView):
    @csrf_exempt
    def post(self,request,cart_token=''):
        cart = get_cart(request,None)
        if request.data['variant'] !="":
            
            variant = Variant.objects.get(pk=request.data['variant'])
            item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, option_type=variant.product.option_type.name, 
                                                        option_value=variant.option_value.value,cost_price=variant.product.cost_price)
            item.quantity = request.data['quantity']
            if int(item.quantity) > variant.stock:
                return Response({'message':'Insufficient stock!', "status": False})
            else:
                item.price = int(item.quantity) * item.variant.price
                item.save()
                return Response({'message':'Item added to cart successfully.', "status": True})   

        else:
            product = Product.objects.get(pk=request.data['product_id'])
            item, created = CartItem.objects.get_or_create(cart=cart,product=product,quantity=request.data['quantity'],price= product.price,cost_price=product.cost_price)
            item.current_stock = request.data['quantity']

            if int(item.current_stock) > product.current_stock:
                return Response({'message':'Insufficient stock!', "status": False})
            else:
                item.price = int(item.current_stock) * product.price
                item.save()
                return Response({'message':'Item added to cart successfully.', "status": True,'cart-':str(cart.token)})

class RemoveCartItemView(APIView):
    
    def delete(self, request, pk):
        # cart = get_cart(request,None)
        cart_item = CartItem.objects.get(pk=pk)
        cart_item.delete()
        return Response({'message':'Cart item removed successfully.', "status": True})
 
class CheckoutView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def post(self,request):
        cart = get_cart(request,None)
        
        if request.method == 'POST':
            # try:
            stripe_order_token = request.data['stripe_token']
            self.initiate_transaction = InitiateTransaction(cart,stripe_order_token)
            time_sent = get_currrent_date_time()
            charge = self.initiate_transaction.create_charge() #UNCOMMENT IN PRODUCTION
            log.info("Charge ",str(charge))
        
            time_arrived = get_currrent_date_time()
            time_range = [time_sent,time_arrived]
            
            if charge['status'] == 'succeeded':
                order = Order(user=request.user)
                order.item_total = cart.total()
                order.total = cart.grand_total()
                order.endless_factory_cut = cart.endless_factory_cut()
                
                order.shipping_address = Address.objects.filter(pk=request.data['address_id']).first()
                number = order.save()
                order.set_line_items_from_cart(cart,number,request.user)
                order.set_transaction(request.user, charge, request.data['card_number'], request.data['save_card'],time_range)
                cart.reset()
                return Response({'receipt':charge['receipt_url'],'message': 'Your order has been placed successfully.', 'status': True, 'order_id': order.number})
            else:
                return Response({'message':'Your card was declined.', 'status': 'error'})
            # except Exception as e:
            #     log.warning(e)
            #     return Response({'error':str(e),'message':'An error occured', 'status': 'error'})


class OrderStatusView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request, pk):
        product_categories = Category.objects.all().order_by('?')[:8]
        cart = get_cart(request,None)
        order_item = LineItem.objects.select_related('order').filter(order__user_id=request.user.id, pk=pk).first()
        if order_item != None:
            context =  {'categories': product_categories, 'lang': get_user_locale(request), 'page_title': 'Order Item #' + str(order_item.id) + ' Status', 'cart':cart, 'order_item': order_item}
            return Response({'data':context, 'status': True})
        else:
            return Response({'message':'Invalid Order', 'status': False})

class WishListView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request):
        wishlisted_products = request.user.wishlistedproduct_set.all()
        page_title = 'Wishlisted Products' 
        product_categories = Category.objects.all().order_by('?')[:8]
        context = {'categories': product_categories, 'lang': get_user_locale(request), 'wishlisted_products': wishlisted_products, 
                   'page_title': page_title, 'cart': get_cart(request,None),'status':True}
        return  Response(context)

    def post(self,request, pk):
        product = Product.objects.get(pk=pk)
        wishlist_product, created = WishlistedProduct.objects.get_or_create(product=product, user=request.user)
        Response({'redirect_url':product.slug,'message':'Product added to wishlist successfully','status':True})

    def delete(self,request, pk):
        product = Product.objects.get(pk=pk)
        wishlist_product = WishlistedProduct.objects.filter(product=product, user=request.user).first()
        if wishlist_product != None:
            wishlist_product.delete()
        Response({'redirect_url':product.slug,'message':'Product removed from wishlist successfully','status':True})


class OrdersView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        
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

            order_items = LineItem.objects.select_related('order', 'variant','product').filter(order__user_id=request.user.id)
            serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'order_items': serializer.data})  
        
        

def set_locale(request):
  current_path = request.GET['current_path'] if request.GET['current_path'] != None else '/'
  locale = request.GET['locale'] if request.GET['locale'] != None else 'en'
  response = redirect(current_path)
  response.set_cookie('locale', locale)  
  return response

# Private methods =========================
def get_cart(request,cart_token):
    token = request.data.get('cart_token') or cart_token
    user_cart, created = Cart.objects.get_or_create(token=token)
    return user_cart

# Private methods =========================
# def get_cart(request):
#     print(request.user.id,request.user.id)
#     response = None
#     if request.user.id != None:
#         user = request.user
#         user.cart_token = user.cart_token if user.cart_token != None  else get_random_string(length=32)
#         user.save()
#         cart, created = Cart.objects.get_or_create(token=user.cart_token)
#         print("Authenticated user cart ", cart)
#     else:
#         token = get_authorization_token(request,False)
#         if token is not False:
#             cart, created = Cart.objects.get_or_create(token=token)
            
#         if token is False:
#             cart_token_jwt,cart_token,cart = decode_access_token(token,True)
#             response = Response()
#             response.set_cookie(key='cart_token',value=cart_token_jwt, samesite=None, httponly=True)
            
#     return cart,response

    
def set_shipping_address_for_order(self,request, order):
    if request.data.get('selected_address') != 'selected_address':
        shipping_address = Address(
            first_name = request.data.get('shipping_first_name'), 
            last_name = request.data.get('shipping_last_name'), 
            line_1 = request.data.get('shipping_address_line_1'), 
            line_2 = request.data.get('shipping_address_line_2'), 
            city = request.data.get('shipping_city'),
            state = request.data.get('shipping_state'), 
            zipcode = request.data.get('shipping_zipcode'), 
            country = request.data.get('shipping_country')
        )
        shipping_address.save()
        request.user.addresses.add(shipping_address)
        return shipping_address
    else:
        shipping_address = Address.objects.filter(pk=request.data.get('selected_address')).first()
        return shipping_address

def product_variants(request, product):
    data = []
    for variant in product.variant_set.all():
        data.append({
            'id': variant.id,
            'option_value': variant.option_value.value,
            'stock': variant.stock
        })
    return data
    
def is_product_wishlisted(request, product):
    if request.user.is_authenticated:
        return product in request.user.wishlisted_products()
    else:
        return False

def get_user_locale(request):
  try:
    return request.COOKIES['locale']
  except:
    return 'en'