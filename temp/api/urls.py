from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from . import views

urlpatterns = [
  path('user/signup', views.signup),
  path('user/login', views.login),
  path('user/orders', views.orders),

  path('user/addresses', views.addresses),
  path('user/wishlisted_products', views.wishlistedproducts),
  path('user/addresses/<int:pk>', views.address),
  
  path('user/credit_cards', views.credit_cards),
  path('user/credit_cards/<int:pk>', views.credit_card),
  path('user/preferred-address', views.preferred_address),

  path('user/profile', views.user_profile),
  path('user/change_password', views.change_password),
  path('user/wishlisted_products/add_product', views.mark_product_wishlisted),
  path('user/wishlisted_products/remove_product', views.mark_product_unwishlisted),

  path('seller/orders', views.seller_orders),
  path('seller/products', views.seller_products),
  path('seller/products/form-data', views.product_form_data),
  path('seller/products/<int:pk>', views.seller_product),
  path('seller/products/<int:pk>/variants', views.product_variants),
  path('seller/products/<int:pk>/images', views.product_images),
  path('seller/products/images/<int:pk>/delete', views.delete_product_image),

  path('seller/products/<int:pk>/reviews', views.product_reviews),
  path('seller/products/variants/<int:pk>', views.update_variant),

  path('forgot_password/request_otp', views.request_otp),
  path('forgot_password/validate_otp', views.validate_otp),
  path('forgot_password/reset_password', views.reset_password),

  path('home', views.home_data),
  path('seller/home', views.seller_home_data),
  path('categories', views.categories),
  path('categories/<slug:slug>', views.category),

  path('option_values', views.option_values),

  path('products', views.products),
  path('products/new_arrivals', views.new_arrivals_products),
  
  path('products/<slug:slug>', views.product),

  path('cart', views.cart),
  path('cart/add_item', views.add_item_to_cart),
  path('cart/update_item/<int:pk>', views.update_cart_item),
  path('cart/remove_item/<int:pk>', views.remove_item_from_cart),

  path('checkout', views.checkout),
  
  path('reviews', views.reviews),

]
