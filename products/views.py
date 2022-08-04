from collections import namedtuple
import json
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare
from endless_admin.translations import get_translations
from endless_factory_api.serializers import *
from marketing.models import Campaign
from decorators import unnauthenticate_user, allowed_users, authorize_seller
from datetime import datetime, timezone
from django.db.models import Q
import django_filters
from products.models import Category, Tag, Product, Variant, Attachment, OptionType, OptionValue
from orders.models import Cart, Order, LineItem, Transaction
from accounts.models import User, WishlistedProduct, UserProduct

class NewArrivalProducts(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def new_arrivals_products(request):
        products = Product.objects.filter(is_active=True, approved=True,new_arrival=True)
        serializer= ProductSerializer(products, many=True)
        return Response(serializer.data)

class Products(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def product(request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        serializer= ProductSerializer(product, many=False)
        
        product_variant = Variant.objects.filter(product_id=product.id)

        has_bought_the_product = LineItem.objects.select_related('order').filter(order__user_id=request.GET['user_id'], variant__in=product_variant).count() > 0 if request.GET['user_id'] != None else False
        has_reviewed_the_product = Review.objects.filter(user_id=request.GET['user_id'], product_id=product.id).count() > 0 if request.GET['user_id'] != None else False

        return Response({'product':serializer.data, 'has_bought_the_product': has_bought_the_product, 'has_reviewed_the_product': has_reviewed_the_product})

