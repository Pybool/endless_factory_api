from itertools import product
import json
import logging
from endless_factory_api.paginationclasses import HeaderLimitOffsetPagination
log = logging.getLogger(__name__)
from collections import namedtuple
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import JWTAuthenticationMiddleWare, decode_access_token, get_authorization_token
from endless_admin.translations import get_translations
from endless_factory_api.serializers import *
from marketing.models import Campaign
from decorators import unnauthenticate_user, allowed_users, authorize_seller
from datetime import datetime, timezone
from django.db.models import Q 
from products.models import Category, ProductCountViews, Tag, Product, Variant, Attachment, OptionType, OptionValue
from orders.models import Cart, Order, LineItem, Transaction
from accounts.models import User, WishlistedProduct, UserProduct
from rest_framework.pagination import LimitOffsetPagination
from endless_factory_api.custompagination import CustomPaginatorClass


class NewArrivalProducts(APIView):
    
    def get(self,request):
        
        products = Product.objects.filter(is_active=True, approved=True).order_by('-id')[:20]
        serializer= ProductSerializer(products, many=True)
        return Response({"products":serializer.data,"message":"New arrivals retreived","status":True})


def get_recently_viewed(logged_in, user):
        if logged_in:
            try:
                product_list = []
                products = ProductCountViews.objects.filter(user=user.id).distinct().values('product').order_by('id')
                for product in products:
                    product_list.append(Product.objects.get(id=product.get('product')))
                return product_list
            except Exception as e:
                return []
        
        else:
            try:
                product_list = []
                products = ProductCountViews.objects.filter(session=user).distinct().values('product').order_by('id')
                for product in products:
                    product_list.append(Product.objects.get(id=product.get('product')))
                return product_list
            except:
                return []
            
class RecentlyViewed(APIView):
    
    def get(self,request):
        
        user = None
        anonymous_user = None
        token = get_authorization_token(request,True)
        user_id = decode_access_token(token)
    
        user = User.objects.filter(id=user_id).first() or user
        if user is not None:
            products = get_recently_viewed(True,user)
            serializer= ProductSerializer(products, many=True)
            return Response({"products":serializer.data,"message":"Recently viewed products for logged in user","status":True})

        else:
            if not request.session.session_key:
                request.session.save()
            anonymous_user = request.session.session_key
            if anonymous_user is not None:
                products = get_recently_viewed(False,anonymous_user)
                serializer= ProductSerializer(products, many=True)
                return Response({"products":serializer.data,"message":"Recently viewed products for anonymous user","status":True})


class SingleProduct(APIView):
    
    def get(self,request):
        
        user = None
        slug = request.GET.get('slug','') 
        variant_id = request.GET.get('variant_id','') 
        token = get_authorization_token(request,True)
        user_id = decode_access_token(token)
        product = Product.objects.get(slug=slug)
        anonymous_user = None
        try:
            user = User.objects.get(id=user_id) 
            if user is not None:
                try:
                    product_stats = ProductCountViews.objects.filter(user=user.id,product_id=product.id,slug=slug).first()
                    if product_stats == None:
                        count = 0
                        ProductCountViews.objects.create(user=user.id,product=product,slug=slug,view_counts=count + 1)
           
                    else:
                        ProductCountViews.objects.filter(user=user.id,product=product).update(view_counts=product_stats.view_counts + 1)
                        
                except Exception as e:
                    count = 0 
                    ProductCountViews.objects.create(user=user.id,product=product,slug=slug,view_counts=count + 1)
                    
        except:
            if not request.session.session_key:
                request.session.save()
            anonymous_user = request.session.session_key
            if anonymous_user is not None:
                try:
                    product_stats = ProductCountViews.objects.filter(session=anonymous_user,product_id=product.id,slug=slug).first()
                    if product_stats == None:
                        count = 0
                        ProductCountViews.objects.create(session=anonymous_user,product=product,slug=slug,view_counts=count + 1)
                    else:
                        print(product_stats,product_stats)
                        ProductCountViews.objects.filter(session=anonymous_user,product=product).update(view_counts=product_stats.view_counts + 1)
                        
                except Exception as e:
                    count = 0 
                    ProductCountViews.objects.create(session=anonymous_user,product=product,slug=slug,view_counts=count + 1)

        if anonymous_user is not None:
            product_stats = ProductCountViews.objects.filter(session=anonymous_user,product_id=product.id,slug=slug).values('view_counts')
        
        if user is not None:
            product_stats = ProductCountViews.objects.filter(user=user.id,product_id=product.id,slug=slug).values('view_counts')
        
        distinct_users_views = ProductCountViews.objects.filter(product_id=product.id,slug=slug).count()
        serializer= ProductSerializer(product, many=False)
        product_views_statistics = {"current_user_view":product_stats,"distinct_users_views":distinct_users_views}
        product_variant = Variant.objects.filter(product_id=product.id)
        has_bought_the_product = False
        self.product_reviews = ProductReviews()
        
        try:
            request.user.id = user.id
            product_ids, variant_ids = self.product_reviews.get_user_reviewable_products(request) 
            has_bought_the_product = True if product.id in product_ids else has_bought_the_product
            has_reviewed_the_product = Review.objects.filter(user_id=user.id, product_id=product.id).count() > 0 if user.id != None else False
            viewed = get_recently_viewed(True,user)
            viewed_serializer = ProductSerializer(viewed,many=True)
            return Response({'product':serializer.data,'recently_viewed':viewed_serializer.data, 'has_bought_the_product': has_bought_the_product, 'has_reviewed_the_product': has_reviewed_the_product,'product_views_statistics':product_views_statistics})
        
        except Exception as e:
            log.info(str(e))
            viewed = get_recently_viewed(False,anonymous_user)
            viewed_serializer = ProductSerializer(viewed,many=True)
            return Response({'product':serializer.data,'recently_viewed':viewed_serializer.data, 'has_bought_the_product': str(e), 'has_reviewed_the_product': "N/A",'product_views_statistics':'N/A'})
        
      
            
class Products(APIView):
    pagination_class = LimitOffsetPagination
    
    def get(self,request):
        categories_tuple = []
        categories = Category.objects.all().values_list('id','name')#SubcategoryChoices(Category)
        
        for category in list(categories):
            padded_cat = category
            categories_tuple.append(padded_cat)
        
        self.custom_paginator = CustomPaginatorClass(Products.pagination_class,request)
        q_products = Product.objects.filter(is_active=True, approved=True,featured=True)
        products = self.custom_paginator.paginate_queryset(q_products)
        response = Response({"status":False,"message":"No products to display"})
        
        if products is not None:
            serializer= ProductSerializer(products, many=True)
            response =  self.custom_paginator.get_paginated_response(serializer.data)
            response.data['categories'] =str(tuple(categories_tuple))
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
        lookups =   Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(description__icontains=q) | Q(business_source__icontains=q) | Q(product_type__icontains=q) | Q(slug__icontains=q) | Q(search_tags__name__icontains=q) | Q(search_tags__slug__icontains=q)
        q_products = Product.objects.filter(is_active=True, approved=True,featured=True).filter(lookups).distinct() #Production
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

class FilteredSearchProducts(APIView) :
    
    def get(self,request)-> Response: 
        q = request.GET.get('q')
        lookups =  Q(category__in=list(q)) | Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(description__icontains=q) | Q(business_source__icontains=q) | Q(product_type__icontains=q) | Q(slug__icontains=q | Q(search_tags__icontains=q))
        products = Product.objects.filter(is_active=True, approved=True,featured=True).filter(lookups)
        serializer= ProductSerializer(products, many=True)
        response = {"message":"Search Products results","products":serializer.data,"status":True}
        return Response(response)

class CategorySearchProducts(APIView) :
    
    def node_iterator(self,ids):
        try:
            for id in ids:
                res = Category.objects.filter(parent=int(id[0])).distinct().values_list('id')
                if len(res) > 0:
                    self.node_iterator(res)
                else:
                    if isinstance(id,int):
                        self.leaf_nodes.append(id)
                    else:
                        self.leaf_nodes.append(id[0])
            return True
        
        except:
            return False
    
    def get(self,request)-> Response: 
        q = request.GET.get('q')
        id = get_object_or_404(Category,slug=q).id
        self.subcategories = Category.objects.filter(parent=id).distinct().values_list('id')
        self.leaf_nodes = []
        
        if len(self.subcategories) > 0:
            try:
                itr_res = self.node_iterator(self.subcategories)
                if not itr_res:
                    response = {"message":"An error occured while retrieving category leaf nodes", "status":itr_res}
                    return Response(response)
            except:
                pass
        else:
            if isinstance(id,int):
                self.leaf_nodes.append(id)
            else:
                self.leaf_nodes.append(id[0])
        print(self.leaf_nodes)
        lookups =  Q(category__in=self.leaf_nodes)
        products = Product.objects.filter(is_active=True, approved=True,featured=True).filter(lookups)[:300]
        serializer= ProductSerializer(products, many=True)
        response = {"message":"Category Products leaf nodes","products":serializer.data, "leaf_nodes":self.leaf_nodes,"category_branches":self.subcategories, "status":True}
        return Response(response)
    
            
class ProductReviews(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
        
    def post(self,request) -> Response:
    
        review_comment = request.data.get('review_comment')
        rating = request.data.get('rating')
        is_variant = request.data.get('is_variant') # SET TO 'FALSE' TO DISABLE REVIEWS FOR VARIANT
        variant_id = request.data.get('variant_id') 
        product_id = request.data.get('product_id')
        
        print(is_variant,product_id,variant_id,rating,review_comment)
        
        products, variants = self.get_user_reviewable_products(request)
        
        if is_variant.lower() == 'false' and product_id in products:
            product = Product.objects.get(id=product_id)
            check_user_rated = Review.objects.filter(user=request.user,product=product).first()
            # if check_user_rated is None:
            Review.objects.create(product=product,user=request.user,review=review_comment,rating=rating)
            return Response({'message':'Review was successful','status':True})

            # return Response({'message':'You have already reviewed this product','status':False})
        
        if is_variant.lower() == 'true' and variant_id in variants:
            """THE BELOW BLOCK OF CODE IS EXPERIMENTAL, AS TO DECIDE IF VARIANTS CAN BE REVIEWED OR NOT, FOR NOW THEY CANT SO THE CODE BELOW DOESNT EXECUTE AT ALL YET"""
            variant = Variant.objects.get(id=variant_id)
            check_user_rated = Review.objects.filter(user=request.user,variant=variant).first()
            # if check_user_rated is None:
            Review.objects.create(variant=variant,user=request.user,review=review_comment,rating=rating)
            return Response({'message':'Review for product variant was successful','status':True})

            # return Response({'message':'You have already reviewed this product variant','status':False})

        else:
            return Response({'message':'Please buy this product before reviewing','status':False})
    
    def get_user_reviewable_products(self,request) -> tuple:
    
        all_bought_products = LineItem.objects.select_related('variant','product').filter(order__user_id=request.user.id, order_status="Delivered").values('product_id','variant_id')
        print("all ", all_bought_products)
        product_ids = []
        variant_ids = []
        for item in list(all_bought_products):
            for k,v in item.items():
                if k == 'product_id' and v is not None:
                    product_ids.append(v)
                if k == 'variant_id' and v is not None:
                    variant_ids.append(v)
        log.info(str(set(product_ids)))
        log.info(str(set(variant_ids)))
        log.info("All "+str(all_bought_products))
        return product_ids, variant_ids