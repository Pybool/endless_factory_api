from django.urls import path

from frontend import views

urlpatterns = [
    path('', views.home, name='frontend_home'),
    
    path('users/profile', views.profile, name='frontend_user_profile'),
    path('users/change_password', views.change_password, name='frontend_user_change_password'),

    path('users/orders', views.user_orders, name='user_orders'),
    path('users/wishlisted_products', views.wishlisted_products, name='user_wishlisted_products'),
    path('users/credit_cards', views.credit_cards, name='user_credit_cards'),
    path('select-locale', views.set_locale),
    path('products', views.products, name='products'),
    path('products/<slug:slug>', views.product, name='product'),
    path('variants/<int:pk>/add-to-wishlist', views.add_variant_to_wishlist, name='add_variant_to_wishlist'),
    path('variants/<int:pk>/remove-from-wishlist', views.remove_variant_from_wishlist, name='remove_variant_from_wishlist'),

    path('cart', views.cart, name='cart'),
    path('cart/add_item', views.add_item_to_cart, name='add_item_to_cart'),
    path('cart/update_item/<int:pk>', views.update_cart_item, name='update_cart_item'),
    path('cart/remove_item/<int:pk>', views.remove_item_from_cart, name='remove_item_from_cart'),

    path('orders/checkout', views.checkout, name='checkout'),
    path('order_items/<int:pk>/status', views.order_status, name='order_status')

]
