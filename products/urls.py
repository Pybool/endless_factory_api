
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from .import views

urlpatterns = [
    path('single_product/', views.SingleProduct.as_view()),
    path('products_listings', views.Products.as_view()),
    path('products/search', views.SearchProducts.as_view()),
    path('product/single_product_review/', views.ProductReviews.as_view()),
    path('products/newarrivals', views.NewArrivalProducts.as_view()),
    path('products/recently_viewed', views.RecentlyViewed.as_view()),
    path('products/category_search', views.CategorySearchProducts.as_view()),
    
    
    
    
]