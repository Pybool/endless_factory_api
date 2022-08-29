import logging

from endless_factory_api.paginationclasses import HeaderLimitOffsetPagination

log = logging.getLogger(__name__)
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
from products.models import Category, Tag, Product, Variant, Attachment, OptionType, OptionValue
from orders.models import Cart, Order, LineItem, Transaction
from accounts.models import User, WishlistedProduct, UserProduct
from rest_framework.pagination import LimitOffsetPagination
from endless_factory_api.custompagination import CustomPaginatorClass

    
class NewArrivalProducts(APIView):
    
    # authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        # products = Product.objects.filter(is_active=True, approved=True).order_by('-id')[:10]
        products = Product.objects.filter().order_by('-id')[:10]
        serializer= ProductSerializer(products, many=True)
        return Response({"products":serializer.data,"message":"New arrivals retreived","status":True})

class SingleProduct(APIView):
    
    def get(self,request, slug):
        # product = get_object_or_404(Product, slug=slug, is_active=True)
        product = get_object_or_404(Product, slug=slug)

        serializer= ProductSerializer(product, many=False)
        
        product_variant = Variant.objects.filter(product_id=product.id)
        has_bought_the_product = LineItem.objects.select_related('order').filter(order__user_id=request.user.id, variant__in=product_variant).count() > 0 if request.user.id != None else False
        has_reviewed_the_product = Review.objects.filter(user_id=request.user.id, product_id=product.id).count() > 0 if request.user.id != None else False

        return Response({'product':serializer.data, 'has_bought_the_product': has_bought_the_product, 'has_reviewed_the_product': has_reviewed_the_product})

class Products(APIView):
    pagination_class = LimitOffsetPagination
    
    def get(self,request):
        
        self.custom_paginator = CustomPaginatorClass(Products.pagination_class,request)
        # q_products = Product.objects.filter(is_active=True, approved=True,featured=True)
        q_products = Product.objects.filter()
        products = self.custom_paginator.paginate_queryset(q_products)
        if products is not None:
            serializer= ProductSerializer(products, many=True)
            response =  self.custom_paginator.get_paginated_response(serializer.data)
            response.data['status'] = True
            response.data['products'] = response.data.pop('results')
            response.data['results_count'] = len(q_products)
            response.data["message"] = "Products listings" if response.data['results_count'] != 0 else f"No product was found"
        return response
    
class SearchProducts(APIView):
    pagination_class = LimitOffsetPagination
    
    def get(self,request): 
        self.custom_paginator = CustomPaginatorClass(SearchProducts.pagination_class,request)
        q = request.GET.get('q')
        lookups =  Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(description__icontains=q) | Q(business_source__icontains=q) | Q(product_type__icontains=q) | Q(slug__icontains=q) | Q(search_tags__name__icontains=q) | Q(search_tags__slug__icontains=q)
        # q_products = Product.objects.filter(is_active=True, approved=True,featured=True).filter(lookups) #Production
        q_products = Product.objects.filter(lookups).distinct() #postgresql .distinct('id') # Development # Development
        products = self.custom_paginator.paginate_queryset(q_products)
        
        if products is not None:
            serializer= ProductSerializer(products, many=True)
            response =  self.custom_paginator.get_paginated_response(serializer.data)
            response.data['status'] = True
            response.data['query'] = q
            response.data['products'] = response.data.pop('results')
            response.data['results_count'] = len(q_products)
            response.data["message"] = "Search Products results" if response.data['results_count'] != 0 else f"No search results were found for {q}"
        return response

class FilteredSearchProducts(APIView):
    
    def get(self,request): 
        q = request.GET.get('q')
        lookups =  Q(category__icontains=q) | Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(description__icontains=q) | Q(business_source__icontains=q) | Q(product_type__icontains=q) | Q(slug__icontains=q | Q(search_tags__icontains=q))
        products = Product.objects.filter(is_active=True, approved=True,featured=True).filter(lookups)
        serializer= ProductSerializer(products, many=True)
        response = {"message":"Search Products results","products":serializer.data,"status":True}
        return Response(serializer.data)
