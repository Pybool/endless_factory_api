import json
import logging

from order_tracking.models import OrderTracking
log = logging.getLogger(__name__)
import uuid, time
from django.conf import settings
from django.http import HttpResponse
from accounts.authentication import JWTAuthenticationMiddleWare, decode_access_token, get_authorization_token
from rest_framework.response import Response
from accounts.models import  User
from dashboard.transactions import InitiateTransaction
from endless_factory_api.serializers import LineItemIndexSerializer, OrderTrackingLineItemSerializer, OrderTrackingSerializer
from orders.models import Order, LineItem, Cart, CartItem
from rest_framework.views import APIView


class OrderTrackingView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request):
        order_number = request.GET.get('order_number')
        tracking_number =  request.GET.get('tracking_number')
        
        if tracking_number != '':
            trackable = OrderTracking.objects.filter(tracking_number=tracking_number).first()
            order_track_details = OrderTrackingSerializer(trackable).data
            
            line_item = LineItem.objects.filter(tracking_number=tracking_number).values('order_number','tracking_number','order_status', 'business_source', 'order_status_desc', 'expected_delivery_timeframe')
            
        elif order_number != '':
            order_track_details = LineItem.objects.filter(order_number=order_number)
            order_track_details = OrderTrackingLineItemSerializer(order_track_details).data
            
        if order_track_details != None:
            return Response({'data':{"item":line_item, 'tracking_info': order_track_details}, 'status': True})
        else:
            return Response({'message':'No order found for information supplied', 'status': False})