import logging
from re import search
from notifications.models import Notifications

from order_tracking.models import OrderTracking
log = logging.getLogger(__name__)
from collections import namedtuple
import os, json
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from dashboard.models import Refunds
from endless_admin.translations import get_translations
from endless_factory_api.serializers import AddressSerializer, CampaignSerializer, CategorySerializer, CreateVariantSerializer, CreditCardSerializer, LineItemIndexSerializer, LineItemIndexSerializerDashboard, LineItemPriceIndexSerializer, LineItemProductSerializer, NewAttachmentSerializer, NewCategorySerializer, NewOptionTypeSerializer, NewOptionValueSerializer, NewProductSerializer, NewRefundSerializer, OptionTypeSerializer, OptionValueSerializer, ProductIndexSerializer, ProductSerializer, AdsSerializer, RefundSerializer, TagSerializer, UserAllSerializer, UserSerializer, UserShowSerializer, VariantSerializer, VariantUpdateSerializer, WishlistedProductSerializer
from helpers import Datetimeutils, get_timezone_datetime
from marketing.models import Campaign
from decorators import unnauthenticate_user, allowed_users, authorize_seller
from django.contrib import messages
from datetime import datetime, timezone
from .transactions import RefundTransactions
from django.db.models import Q
import django_filters
# from .forms import CategoryForm, TagForm, ProductForm, VariantForm, AttachmentForm, UserForm, UserProfileForm, CreditCardForm, AddressForm, OptionTypeForm, OptionValueForm
from products.models import Category, Tag, Product, Variant, Attachment, OptionType, OptionValue
from orders.models import Cart, Order, LineItem, Transaction
from accounts.models import CreditCard, IDCardsAttachment, ProofBusinessAttachment, User, WishlistedProduct, Address, UserProduct
# from endless_admin.translations import get_translations
from dotenv import load_dotenv
from tasks.__task__email import *
from django.db import transaction

load_dotenv()
refresh_jwt_token_life = int(os.getenv("REFRESH_JWT_TOKEN_LIFE"))
ISSUER_NAME = os.getenv("2FA_ISSUER_NAME")


def get_user_locale(request):
    try:
        return request.COOKIES['locale']
    except:
        return 'en'

def send_mail(data):
    mail = {"message":data['message'],
            "subject":data['subject'],
            "sender":ISSUER_NAME,
            "recipient":data['user'].email}
    send_order_status_mail_task.delay(mail)
    
class HomeView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self, request):
        context = {'section_active': 'dashboards', 'lang': get_user_locale(request)}
        if request.user.is_admin():
            context['recent_orders'] = LineItem.objects.select_related('order', 'variant')
        elif request.user.is_seller():
            seller_product_variants = Variant.objects.filter(product__in=request.user.products())
            context['recent_orders'] = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
        return Response({"status":True,"context":context})

class ProfileView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    def get(self,request):
        user = request.user
        serializer= UserSerializer(user, many=False)
        return Response({'user': serializer.data, "status": True})
    
    def put(self,request):
        if request.method == 'PUT':
            user = request.user
            serializer = UserSerializer(user,data=request.data)
            if serializer.is_valid():
                 serializer.save()
                 return Response({"status":True,"message": get_translations('Account was updated successfully', get_user_locale(request))})
            else:
                return Response({"status":False,"message": get_translations('Account updation failed', get_user_locale(request))})

#Users CRUD ================
class UsersView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def get(self,request):
        users = User.objects.all()
        serializer= UserShowSerializer(users, many=True)
        context = {'users': serializer.data, 'section_active': 'users', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})
    

class AllUsersWishlistedProductsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def get(self,request):
        wishlisted_products = WishlistedProduct.objects.all()
        serializer= WishlistedProductSerializer(wishlisted_products, many=True)
        context = {'wishlisted_products': serializer.data, 'section_active': 'users_wishlisted_products', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})
      
class NewUserView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    @authorize_seller()
    def post(self,request):
        data = request.data
        response = {}
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()
            instance.save()
            response['status'] = True
            response['email'] = instance.email
            response['message'] = get_translations('User created successfully', get_user_locale(request))
            return Response(response)
        else:
            data = serializer.errors
            return Response({'status': False, 'errors': data})
    
class EditUserView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    @authorize_seller()
    def post(self,request,pk):
        response = {}
        if request.method == 'POST':
            user = get_object_or_404(User, pk=pk)
            serializer= UserAllSerializer(user, data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                if request.data['password'] is not None:
                    instance.set_password(request.data['password'])
                    instance.save()
                response['status'] = True
                response['email'] = instance.email
                response['message'] = get_translations('User updated successfully', get_user_locale(request))
            return Response(response)

class SingleUsersAddressesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def get(self,request,pk):
        
        data = Address.objects.filter(user=pk)
        serializer= AddressSerializer(data, many=True)
        context = {'addresses': serializer.data, 'section_active': 'addresses', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})

class NewUsersAddressesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def post(self,request,pk):
        if request.method == 'POST':
            request.data['user'] = pk
            serializer= AddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {'message':get_translations('User address created successfully', get_user_locale(request)),'section_active': 'addresses', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'}) 
              
class EditUsersAddressesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def put(self,request,pk,address_id):
        if request.method == 'PUT':
            address = get_object_or_404(Address, pk=address_id)
            serializer= AddressSerializer(address, data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {'message':get_translations('User address updated successfully', get_user_locale(request)),'section_active': 'addresses', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'}) 

class SingleUsersCreditCardsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def get(self,request,pk):        
        data = CreditCard.objects.filter(user=pk)
        serializer= CreditCardSerializer(data, many=True)
        context = {'creditcards': serializer.data, 'section_active': 'creditcards', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})
    
class VerifySellerBusinessView(APIView):
    
    def get(self,request,pk):
        seller = User.objects.filter(pk=pk).update(biz_info_verified=True,user_type='Both')
        context = {'message':'Seller verified successfully', 'section_active': 'sellers_verification', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})
    
class DeclineSellerBusinessView(APIView):
    
    def get(self,request,pk):
        User.objects.filter(pk=pk).update(biz_info_submitted=False, biz_info_verified=False,user_type='Buyer')
        user = User.objects.get(pk=pk)
        idcard = IDCardsAttachment.objects.get(company=user).delete()
        pob = ProofBusinessAttachment.objects.get(company=user).delete()
        context = {'message':'Seller details was declined', 'section_active': 'sellers_decline', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})

# Orders
########################################################UNTESTED###########################

class Orders(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        item_id = request.GET.get('oid')
        if item_id:
            item = LineItem.objects.get(pk=item_id)
            serializer = LineItemIndexSerializer(item)
            context = {"item": serializer.data, 'section_active': 'orders', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": True})
        else:
            if request.user.is_admin():
                order_items = LineItem.objects.select_related('variant')
                serializer = LineItemIndexSerializer(order_items,many=True)
                context =  {"order_items": serializer.data, 'section_active': 'orders', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            
            elif request.user.is_seller():
                seller_product_variants = Variant.objects.filter(product__in=request.user.products())
                order_items = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
                serializer = LineItemIndexSerializer(order_items,many=True)
                context =  {"order_items": serializer.data, 'section_active': 'orders', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            

class OrdersSearch(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        
        search_string = request.GET.get('search_string', 'None')
        date_filter = request.GET.get('date_filter', 'None')
        status_filter = request.GET.get('status_filter', 'None')
        tracking_number = request.GET.get('tracking_number', 'None')
        log.info(search_string,date_filter,status_filter,tracking_number)
        
        if request.user.is_seller() or request.user.is_admin():
            if search_string is not 'None' and date_filter is 'None' and status_filter is 'None' and tracking_number is 'None':
                user_products = request.user.products()
                product_serializer = ProductIndexSerializer(user_products, many=True)
                seller_product_variants = Variant.objects.filter(product__in=user_products)
                log.info(seller_product_variants[0])
                lookups =  Q(order_number__icontains=search_string) | Q(price__icontains=search_string) | Q(tracking_number__icontains=search_string) | Q(courier_agency__icontains=search_string)
                orders = LineItem.objects.select_related('variant','product').filter(Q(variant__in=seller_product_variants) | Q(product__in=user_products)).filter(lookups)
                order_serializer= LineItemIndexSerializer(orders, many=True)
                return Response({'orders': order_serializer.data, 'products': product_serializer.data})
            
            elif search_string is 'None' and date_filter is not 'None' or status_filter is not 'None' or tracking_number is not 'None':
                
                user_products = request.user.products()
                product_serializer = ProductIndexSerializer(user_products, many=True)
                seller_product_variants = Variant.objects.filter(product__in=user_products)
                log.info(seller_product_variants[0])
                lookups = Q(created_at__icontains=date_filter) |  Q(order_status__icontains=status_filter) | Q(tracking_number__icontains=tracking_number)
                orders = LineItem.objects.select_related('variant','product').filter(Q(variant__in=seller_product_variants) | Q(product__in=user_products)).filter(lookups)
                order_serializer= LineItemIndexSerializer(orders, many=True)
                return Response({'orders': order_serializer.data, 'products': product_serializer.data})


class MarkOrderStatus(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def post(self,request, pk):
        if request.method == 'POST':
            try:
                item = LineItem.objects.get(id=pk)
                comment = request.data.get('comment')
                if item.order_status == request.data['status']:
                        context = {"message":get_translations(f"Order item already marked as {request.data['status']}", get_user_locale(request))}
                        return Response({'context': context, "status": False})
                else:
                    item.order_status = request.data['status']
                    item.updated_at = get_timezone_datetime()
                    if request.data['status'].lower() == "dispatched":
                        ordertracking = item.ordertracking
                        ordertracking.shipped_at = str(get_timezone_datetime())
                        ordertracking.dispatched_comment = comment
                        ordertracking.active_status = "Dispatched"
                        ordertracking.save()
                        subject = "Item Dispatched"
                        message = comment if comment != None else f"Your Item has been dispatched by {item.business_source}"
                        kwargs = {"tracking_number":item.tracking_number,"user":item.user,"subject":subject,"item":item,"message":message,"created_at":ordertracking.processed_at}
                        Notifications.objects.create(**kwargs)
                        # self.send_notifications(kwargs)
                        
                    elif request.data['status'].lower() == "shipped":
                        item.order.is_shipped = True
                        ordertracking = item.ordertracking
                        ordertracking.shipped_at = str(get_timezone_datetime())
                        ordertracking.shipping_comment = comment
                        ordertracking.active_status = "Shipped"
                        ordertracking.save()
                        subject = "Item Shipped"
                        message = comment if comment != None else f"Your Item has been Shipped by {item.courier_agency}"
                        kwargs = {"tracking_number":item.tracking_number,"user":item.user,"subject":subject,"item":item,"message":message,"created_at":ordertracking.processed_at}
                        Notifications.objects.create(**kwargs)
                        # self.send_notifications(kwargs)
                        
                    elif request.data['status'].lower() == "delivered":
                        item.ordertracking.delivered_at = str(get_timezone_datetime())
                        ordertracking = item.ordertracking
                        ordertracking.delivery_comment = comment
                        ordertracking.active_status = "Delivered"
                        ordertracking.save()
                        subject = "Item Delivered"
                        message = comment if comment != None else f"Your Item has been delivered by {item.courier_agency}"
                        kwargs = {"tracking_number":item.tracking_number,"user":item.user,"subject":subject,"item":item,"message":message,"created_at":ordertracking.processed_at}
                        Notifications.objects.create(**kwargs)
                        # self.send_notifications(kwargs)
                    item.save()
                    
                    context = {"url":"/dashboards/orders?oid=" + str(pk),"message": get_translations(f"Item marked as {request.data['status']} successfully", get_user_locale(request))}
                    return Response({'context': context, "status": True})
            except Exception as e:
                log.info(str(e))
                context = {"url":"/dashboards/orders?oid=" + str(pk),"message": "oops an error occured"}
                return Response({'context': context, "status": False})
        else:
            context = {"url":"/dashboards/orders?oid=" + str(pk),"message": get_translations('Invalid Action Performed', get_user_locale(request))}
            return Response({'context': context, "status": False})


class ProcessOrder(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def post(self,request):
        if request.method == 'POST':
            try:
                start_date = request.data.get('start_date')
                end_date = request.data.get('end_date')
                start_day = request.data.get('start_day')
                end_day = request.data.get('end_day')
                processing_comment = request.data.get('comment')
                processing_comment = None if processing_comment == '' else processing_comment
                expected_delivery_timeframe = f"Your Item is expected to be delivered between {start_day} {start_date} and {end_day} {end_date}"
                
                instance,create = OrderTracking.objects.update_or_create(tracking_number=request.data.get('tracking_number'))
                
                parsed_updated_at =  datetime.strptime(request.data.get('updated_at'), '%d-%m-%Y').replace(tzinfo=timezone.utc)
                LineItem.objects.filter(pk__in=request.data['line_items']).update(ordertracking_id=instance.id,updated_at=parsed_updated_at,
                                                                                    order_status="Processing",
                                                                                    courier_agency=request.data.get('courier_agency'),
                                                                                    tracking_number=request.data.get('tracking_number'),
                                                                                    expected_delivery_timeframe = expected_delivery_timeframe,
                                                                                    )
                
                line_item = LineItem.objects.get(pk__in=request.data['line_items'])
                ordertracking = line_item.ordertracking
                ordertracking.processed_at = str(get_timezone_datetime())
                ordertracking.processing_comment=processing_comment
                # ordertracking.order_created_at = str(line_item.created_at)
                ordertracking.active_status = "Processing"
                ordertracking.save()
                subject = "Item Processing"
                processing_comment = processing_comment if processing_comment != None else f"Your Item is currently being processed by {line_item.business_source}"
                kwargs = {"tracking_number":line_item.tracking_number,"user":line_item.user,"subject":subject,"item":line_item,"message":processing_comment,"created_at":ordertracking.processed_at}
                Notifications.objects.create(**kwargs)
                # self.send_notifications(kwargs)
                context = {"message": get_translations('Item was marked as processing successfully', get_user_locale(request))}
                return Response({'context': context, "status": True})
            except Exception as e:
                context = {"error":str(e),"message": get_translations('Invalid Order Item', get_user_locale(request))}
            return Response({'context': context, "status": False})
        else:
            context = {"message": get_translations('Invalid Action Performed', get_user_locale(request))}
            return Response({'context': context, "status": False})
    
    def send_notification(self,**kwargs):
        return True
    
########################################################UNTESTED###########################

class SellerHomeData(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):

        if request.user.is_seller():
            user_products = request.user.products()
            seller_product_variants = Variant.objects.filter(product__in=user_products)
            log.info("Seller variants "+ str(len(seller_product_variants)))
            
            orders = LineItem.objects.select_related('variant').filter(Q(variant__in=seller_product_variants)|Q(product__in=request.user.products()))
            order_serializer= LineItemIndexSerializer(orders, many=True)
            return Response({'orders': order_serializer.data, 'orders_count': len(orders)})

        elif request.user.is_admin():
            order_items = LineItem.objects.select_related('variant')
            order_serializer= LineItemIndexSerializer(order_items, many=True)
            return Response({'orders': order_serializer.data, 'orders_count': len(order_items)})
            

class SellerProductListings(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):

        if request.user.is_seller():
            user_products = request.user.products()
            product_serializer = ProductSerializer(user_products, many=True)
            return Response({'products': product_serializer.data, 'products_count': len(user_products)})

#####################SELLER DASHBOARD#######################################

class SellerDashboardView(APIView):
    
    def sales_report(self,request, **kwargs):
        
        filter = request.GET.get('filter')
        duration = int(request.GET.get('duration'))
        if request.user.is_seller():
            
            self.datetimeutils = Datetimeutils(duration)
            start_date , end_date = self.datetimeutils.get_pages_created_on_date(filter)
            seller_product_variants = Variant.objects.filter(product__in=request.user.products())
            order_items = LineItem.objects.select_related('variant').filter(Q(variant__in=seller_product_variants,created_at__range=[start_date,end_date])|Q(product__in=request.user.products(),created_at__range=[start_date,end_date])).values('created_at__date').order_by('created_at__date').annotate(Count("id"),day_sales=Sum('price'))
            log.info(str(seller_product_variants)+str(start_date)+str(end_date))
            order_items_cost = sum(order_item['day_sales'] for order_item in order_items)
            
            ########Get Pending and completed orders
            # log.info(LineItem.objects.select_related('product').filter(product__in=request.user.products(),created_at__range=[start_date,end_date]).values('order_status'))
            log.info(LineItem.objects.filter(Q(variant__in=seller_product_variants,created_at__range=[start_date,end_date])|Q(order_status='Delivered') |Q(product__in=request.user.products(),created_at__range=[start_date,end_date])))
            
            duration_uncompleted_orders_counts = LineItem.objects.select_related('variant','product').filter(order_status='Pending').filter(Q(variant__in=seller_product_variants,created_at__range=[start_date,end_date]) |Q(product__in=request.user.products(),created_at__range=[start_date,end_date])).values_list(Sum('price'),Count('id'))
            duration_completed_orders_counts = LineItem.objects.select_related('variant','product').filter(Q(variant__in=seller_product_variants,created_at__range=[start_date,end_date])|Q(order_status='Delivered') |Q(product__in=request.user.products(),created_at__range=[start_date,end_date])).values_list(Sum('price'),Count('id'),Sum('cost_price'))
            duration_completed_orders_counts_cost = sum(duration_completed_orders_counts[0] for duration_completed_orders_counts in duration_completed_orders_counts)
            duration_completed_orders_cost_price_total = sum(duration_completed_orders_counts[2] for duration_completed_orders_counts in duration_completed_orders_counts)
            duration_uncompleted_orders_counts_cost = sum(duration_uncompleted_orders_counts[0] for duration_uncompleted_orders_counts in duration_uncompleted_orders_counts)
                        
            ########Get recent orders#########
            variant_recent_orders =  LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants).order_by('-created_at')[:20]
            recent_orders =  LineItem.objects.select_related('product').filter(product__in=request.user.products()).order_by('-created_at')[:20]
            serializer = LineItemIndexSerializerDashboard(recent_orders,many=True)
            variant_serializer = LineItemIndexSerializerDashboard(variant_recent_orders,many=True)
            return {
                    "status": True,"revenue":order_items_cost,
                    "start_date":start_date, "end_date":end_date,
                    'chart_data':order_items,
                    'pending_orders_data': {'count':len(duration_uncompleted_orders_counts),
                                            'revenue':duration_uncompleted_orders_counts_cost
                                            },
                    'completed_orders_data':{'count':len(duration_completed_orders_counts),
                                            'revenue':duration_completed_orders_counts_cost,
                                            'cost_incurred':duration_completed_orders_cost_price_total,
                                            'earnings':(duration_completed_orders_counts_cost - duration_completed_orders_cost_price_total)
                                            },
                    'recent_orders':serializer.data,
                    'variant_recent_orders':variant_serializer.data,
                    'section_active': 'sales_dashboard',
                    'lang': get_user_locale(request)
                    }
            
        else:
            return{'status':False,"message":"You are not permitted, private endpoint"}
        
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users() 
    def get(self,request):
        response = self.sales_report(request)
        return Response(response)


# #Option Types CRUD ================
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def option_types(request):
#   option_types = OptionType.objects.all()
#   context = {'option_types': option_types, 'section_active': 'option_types', 'lang': get_user_locale(request)}
#   return render(request, 'dashboard/option_types/index.html', context)

class NewOptionTypeView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    @authorize_seller()
    def post(self,request):
        serializer = NewOptionTypeSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            
            serializer.save()
            context = {'message':get_translations('OptionType created successfully', get_user_locale(request)),'section_active': 'categories', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": True})

        return Response({"status": False})
    
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def edit_option_type(request, pk):
#   option_type = OptionType.objects.get(pk=pk)
#   form = OptionTypeForm(instance=option_type)
#   if request.method == 'POST':
#     form = OptionTypeForm(request.POST, instance=option_type)
#     if form.is_valid():
#       form.save()
#       messages.success(request, get_translations('OptionType updated successfully', get_user_locale(request)))
#       return redirect('option_types_list')
#   return render(request, 'dashboard/option_types/edit.html', {'form': form, 'option_type': option_type, 'section_active': 'option_types', 'lang': get_user_locale(request)})

#Option Values CRUD ================
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def option_values(request):
#   option_values = OptionValue.objects.all()
#   if request.GET.get('option_type') is not None:
#     option_values = option_values.filter(option_type=request.GET.get('option_type'))
#     context = {'option_values': option_values, 'section_active': 'option_values', 'lang': get_user_locale(request)}
#     return render(request, 'dashboard/option_values/index.html', context)
#   else:
#     context = {'option_values': option_values, 'section_active': 'option_values', 'lang': get_user_locale(request)}
#     return render(request, 'dashboard/option_values/index.html', context)

class NewOptionValueView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    @authorize_seller()
    def post(self,request):
        serializer = NewOptionValueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context = {'message':get_translations('OptionValue created successfully', get_user_locale(request)),'section_active': 'categories', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": True})

        return Response({"status": False})
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def edit_option_value(request, pk):
#   option_value = OptionValue.objects.get(pk=pk)
#   form = OptionValueForm(instance=option_value)
#   if request.method == 'POST':
#     form = OptionValueForm(request.POST, instance=option_value)
#     if form.is_valid():
#       form.save()
#       messages.success(request, get_translations('OptionValue updated successfully', get_user_locale(request)))
#       return redirect('option_values_list')
#   return render(request, 'dashboard/option_values/edit.html', {'form': form, 'option_value': option_value, 'section_active': 'option_values', 'lang': get_user_locale(request)})

# #Categories CRUD ================
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def categories(request):
#   categories = Category.objects.all()
#   context = {'categories': categories, 'section_active': 'categories', 'lang': get_user_locale(request)}
#   return render(request, 'dashboard/categories/index.html', context)

class NewCategoriesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    @allowed_users()
    @authorize_seller()
    def post(self,request):
        
        serializer = NewCategorySerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            context = {'message':get_translations('Category created successfully', get_user_locale(request)),'section_active': 'categories', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": True})
# @login_required(login_url='login')
# @allowed_users()
# @authorize_seller()
# def edit_category(request, slug):
#   category = Category.objects.get(slug=slug)
#   form = CategoryForm(instance=category)
#   if request.method == 'POST':
#     form = CategoryForm(request.POST, request.FILES, instance=category)
#     if form.is_valid():
#       form.save()
#       messages.success(request, get_translations('Category updated successfully', get_user_locale(request)))
#       return redirect('categories_list')
#   return render(request, 'dashboard/categories/edit.html', {'form': form, 'category': category, 'section_active': 'categories', 'lang': get_user_locale(request)})


#Tags CRUD =================================
class TagsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()  
    @authorize_seller()
    def get(self,request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        context = {'tags': serializer.data, 'section_active': 'tags', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})

    @allowed_users()  
    @authorize_seller()
    def post(self,request):
        if request.method == 'POST':
            serializer= TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {'message':get_translations('Tag created successfully', get_user_locale(request)),'section_active': 'tags', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
    
    @allowed_users()  
    @authorize_seller()
    def put(self,request,slug):
        if request.method == 'PUT':
            tag = get_object_or_404(Tag, slug=slug)
            serializer= TagSerializer(tag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                context = {'message':get_translations('Tag updated successfully', get_user_locale(request)),'section_active': 'addresses', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'}) 

# Products CRUD =================================
class ProductsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def get(self,request):
        products = request.user.products() if request.user.is_seller() else Product.objects.all()
        serializer = ProductSerializer(products,many=True)
        context = {'products': serializer.data, 'section_active': 'products', 'lang': get_user_locale(request)}
        return Response({'context': context, "status": True})


class ProductsformView(APIView):
    
    # authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()  
    def get(self,request):

        categories = Category.objects.all()
        categories_serializer= CategorySerializer(categories, many=True)

        option_types = OptionType.objects.all()
        option_type_serializer = OptionTypeSerializer(option_types, many=True)

        tags = Tag.objects.all()
        tag_serializer = TagSerializer(tags, many=True)

        return Response({'categories': categories_serializer.data, 'option_types': option_type_serializer.data, 'tags': tag_serializer.data, 'status': True})


class OptionValuesView(APIView):
    
    # authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()  
    def get(self,request,optiontype):
        option_type = OptionType.objects.get(pk=optiontype)
        option_values = OptionValue.objects.filter(option_type = option_type)
        option_values_serializer= OptionValueSerializer(option_values, many=True)

        return Response({'option_values':option_values_serializer.data, 'status': True})
          
class NewProductsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request):

        category_id = int(request.GET.get('cat_id'))
        categories = Category.objects.filter(parent=category_id)
        sub_categories_serializer= CategorySerializer(categories, many=True)
        return Response({'sub_categories': sub_categories_serializer.data, 'status': True})

        
    @allowed_users()  
    def post(self,request):
        if request.method == 'POST':
            print("List of images ",request.FILES.getlist('document', None))
            if len(request.FILES.getlist('document', None)) < 1:
                log.info("Uploaded images "+ str(request.FILES.getlist('document', None)))
                return Response({'No image was provided for product': "message", "status": False})
            
            data = json.loads(request.data['data'])
            data['business_source'] = request.user.company_name
            data['account_manager_phone_1'] = request.user.account_manager_phone_1
            data['company_address_1'] = request.user.store_name
            data['company_mailing_address'] = request.user.company_mailing_address
            serializer = NewProductSerializer(data=data)
            
            if serializer.is_valid():
                instance = serializer.save()
                if data['has_variant']:
                    self.createVariants(request,instance,request.data['data'])
                self.saveAttachments(request,instance,json.loads(request.data['data']),request.FILES.getlist('document', None))
                user_product = UserProduct(user_id=request.user.id, product=serializer.instance)
                user_product.save()
                context = {'message':get_translations('Product created successfully', get_user_locale(request)),'section_active': 'products', 'lang': get_user_locale(request)}
                return Response({'context': context, "status": True})
            else:
                return Response({'error': serializer.errors, "status": False})
    
    @allowed_users() 
    def put(self,request):
        slug = request.GET.get('slug')
        product = Product.objects.get(slug=slug)
        if request.method == 'PUT':
            
            search_tags_obj = []
            src_data = json.loads(request.data['data'])
            data = src_data.get('main_product')
            search_tags = src_data.get('search_tags')
            variants = src_data.get('edited_variants')
            new_variants = src_data.get('new_variants')
            request.variants_ids = [ sub['id'] for sub in variants ]
            request.variants_data = variants
            product = Product.objects.get(id=product.id)
            
            Product.objects.filter(id=product.id).update(**data)#Update parent product 
            
            if len(search_tags) > 0: #Update search Tags
                for search_tag in search_tags:
                    search_tags_obj.append(get_object_or_404(Tag,id=search_tag))
                    
                product.search_tags.set(search_tags_obj, clear=True)
            
            if len(variants) > 0: #Update variants
                response = self.updateVariants(request,product)
            
            if len(new_variants) > 0: #Create new variants if user added one
                data['variants'] = new_variants
                self.createVariants(request,product,data)
                
            return Response({'product': str(response)})
        
    def createVariants(self,request,instance,data):
        
        product = Product.objects.get(slug=instance.slug)
        OptionValue.objects.filter(option_type=product.option_type)
        
        if request.method == 'POST' or request.method == 'PUT':
            data = json.loads(request.data['data'])
            log.info({'var': str(data)})
            
            for i in range(0,len(data['variants'])):
                data['variants'][i]['product'] = str(instance.id)
                
            serializer = CreateVariantSerializer(data=data['variants'],many=True)
            if serializer.is_valid():
                print("Serializer data ",serializer.data)
                serializer.save()
    
    def updateVariants(self,request,product):
        
        for idx, variant in enumerate(request.variants_ids):
            variant_obj = get_object_or_404(Variant,id=variant)
        
            serializer= VariantUpdateSerializer(variant_obj, data=request.variants_data[idx])
            if serializer.is_valid():
                serializer.save()
                return {"status": True}
            else:
                return {'errors': serializer.errors, "status": False}
                
    def saveAttachments(self,request,instance,data,files):
        
        if request.method == 'POST':
            print("Files ",files)
            data['product'] = str(instance.id)
            _serializer = NewAttachmentSerializer(data=data,context={'documents': files})
            if _serializer.is_valid():
                _serializer.save()
                
                
#Product Variants CRUD =================================
# @login_required(login_url='login')
# @allowed_users()
# def product_variants(request, slug):
#   product = Product.objects.get(slug=slug)
#   variants = Variant.objects.filter(product=product)
#   context = {'variants': variants, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)}
#   return render(request, 'dashboard/products/variants/index.html', context)

class NewProductVariantView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users() 
    def post(self,request, slug):
        product = Product.objects.get(slug=slug)
        option_values = OptionValue.objects.filter(option_type=product.option_type)

        form = VariantSerializer(request.POST)
        if form.is_valid():
            form.instance.option_value = OptionValue.objects.get(pk=request.POST.get('option_value'))
            form.save()
            messages.success(request, get_translations('Product variant created successfully', get_user_locale(request)))
            return redirect('product_variants_list', product.slug)
        # return render(request, 'dashboard/products/variants/new.html', {'form': form, 'option_values': option_values, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)})


# @login_required(login_url='login')
# @allowed_users()
# def edit_product_variant(request, slug, id):
#   product = Product.objects.get(slug=slug)
#   option_values = OptionValue.objects.filter(option_type=product.option_type)
#   variant = Variant.objects.get(pk=id)
#   form = VariantForm(instance=variant)
  
#   if request.method == 'POST':
#     form = VariantForm(request.POST, instance=variant)
#     if form.is_valid():
#       form.instance.option_value = OptionValue.objects.get(pk=request.POST.get('option_value'))
#       form.save()
#       messages.success(request, get_translations('Product variant updated successfully', get_user_locale(request)))
#       return redirect('product_variants_list', product.slug)
#   return render(request, 'dashboard/products/variants/edit.html', {'form': form, 'option_values': option_values, 'product': product, 'section_active': 'products', 'variant': variant, 'lang': get_user_locale(request)})

# #Product Images CRUD =================================
# @login_required(login_url='login')
# @allowed_users()
# def product_attachments(request, slug):
#   product = Product.objects.get(slug=slug)
#   attachments = Attachment.objects.filter(product=product)
#   context = {'attachments': attachments, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)}
#   return render(request, 'dashboard/products/attachments/index.html', context)

# class NewProductVariantView(APIView):
    
#     authentication_classes = [JWTAuthenticationMiddleWare]
#     @allowed_users() 
#     product = Product.objects.get(slug=slug)
#     form = AttachmentForm()
#     if request.method == 'POST':
#         form = AttachmentForm(request.POST, request.FILES)
#         if form.is_valid():
#         form.save()
#         messages.success(request, get_translations('Product attachment created successfully', get_user_locale(request)))
#         return redirect('product_attachments_list', product.slug)
#     return render(request, 'dashboard/products/attachments/new.html', {'form': form, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)})

# @login_required(login_url='login')
# @allowed_users()
# def edit_product_attachment(request, slug, id):
#   product = Product.objects.get(slug=slug)
#   attachment = Attachment.objects.get(pk=id)
#   form = AttachmentForm(instance=attachment)
#   if request.method == 'POST':
#     form = AttachmentForm(request.POST, request.FILES, instance=attachment)
#     if form.is_valid():
#       form.save()
#       messages.success(request, get_translations('Product attachment updated successfully', get_user_locale(request)))
#       return redirect('product_attachments_list', product.slug)
#   return render(request, 'dashboard/products/attachments/edit.html', {'form': form, 'product': product, 'section_active': 'products', 'attachment': attachment, 'lang': get_user_locale(request)})

# def get_user_locale(request):
#     try:
#         return request.COOKIES['locale']
#     except:
#         return 'en'


#################################CUSTOMERS PAYMENT REFUNDS###########################

class RefundsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users() 
    @authorize_seller() 
    def get(self,request,q='',charge_id='',refund_id='',limit=1000):
        if request.method == 'GET':
            
            singlecharge = True if isinstance(int(q),int) else False   
            self.createrefund = RefundTransactions(charge_id=charge_id,refund_id=refund_id)
            refunds = RefundTransactions.list_refunds(q, data_obj='', singlecharge=singlecharge, limit=limit)
            context = {'data': refunds, 'message':get_translations('Refund list was successfully fetched', get_user_locale(request)),'section_active': 'refundlist', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": True})
        
    @allowed_users() 
    @authorize_seller() 
    def post(self,request):
        if request.method == 'POST':
            
            data = json.loads(request.data['data'])
            charge_id = data['charge_id']
            customer_id = Transaction.get_customer_id_via_charge_id(charge_id)
            self.createrefund = RefundTransactions(charge_id)
            response = self.createrefund.create_refund()
            response_object = namedtuple("Refund", response.keys())(*response.values())
            
            if response_object.status == 'succeeded':
                
                data = {
                        "customer": User.objects.get(id=customer_id),
                        "refund_id":response_object.id,
                        "amount":response_object.amount,
                        "currency":response_object.currency,
                        "related_charge":response_object.charge,
                        "refund_reason":data['reason'],
                        "status":response_object.status
                        }
                serializer = NewRefundSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    context = {'message':get_translations('Refund created successfully', get_user_locale(request)),'section_active': 'refund', 'lang': get_user_locale(request)}
                    return Response({'context': context, "status": True})
            context = {'message':get_translations('Refund could not be completed', get_user_locale(request)),'section_active': 'refund', 'lang': get_user_locale(request)}
            return Response({'context': context, "status": False})