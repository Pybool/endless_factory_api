from django.urls import path

from admin_dashboard import views

urlpatterns = [
    #Admin
    path('dashboards/orders', views.orders, name='dashboard_orders'),
    
    path('home', views.home, name='dashboard_home'),
    path('users/profile', views.profile, name='user_profile'),
    
    # Categories
    path('categories', views.categories, name='categories_list'),
    path('categories/new', views.new_category, name='new_category'),
    path('categories/<slug:slug>/edit', views.edit_category, name='edit_category'),

    # Option Types
    path('option_types', views.option_types, name='option_types_list'),
    path('option_types/new', views.new_option_type, name='new_option_type'),
    path('option_types/<int:pk>/edit', views.edit_option_type, name='edit_option_type'),

    # Option Values
    path('option_values', views.option_values, name='option_values_list'),
    path('option_values/new', views.new_option_value, name='new_option_value'),
    path('option_values/<int:pk>/edit', views.edit_option_value, name='edit_option_value'),

    # Users
    path('users', views.users, name='users_list'),
    path('users/wishlisted_products', views.users_wishlisted_products, name='users_wishlisted_products'),
    path('users/new', views.new_user, name='new_user'),
    path('users/<int:pk>/edit', views.edit_user, name='edit_user'),

    # Addresses
    path('users/<int:pk>/addresses', views.user_addresses, name='user_addresses'),
    path('users/<int:pk>/addresses/new', views.new_user_address, name='new_user_address'),
    path('users/<int:pk>/addresses/<int:address_id>/edit', views.edit_user_address, name='edit_user_address'),

    # Credit Cards
    path('users/<int:pk>/credit_cards', views.credit_cards, name='credit_cards'),

    # Orders
    path('orders', views.orders, name='orders_list'),
    path('items/<int:pk>/mark-shipped', views.mark_item_shipped, name='mark_item_shipped'),

    # path('orders/<str:number>/details', views.orders_show, name='order'),

    # Tags
    path('tags', views.tags, name='tags_list'),
    path('tags/new', views.new_tag, name='new_tag'),
    path('tags/<slug:slug>/edit', views.edit_tag, name='edit_tag'),

    # Products
    path('products', views.products, name='products_list'),
    path('products/new', views.new_product, name='new_product'),
    # path('products/<slug:slug>/edit', views.edit_product, name='edit_product'),

    # Variants
    path('products/<slug:slug>/variants', views.product_variants, name='product_variants_list'),
    path('products/<slug:slug>/variants/new', views.new_product_variant, name='new_product_variant'),
    # path('products/<slug:slug>/variants/<int:id>/edit', views.edit_product_variant, name='edit_product_variant'),

    # Attachments
    path('products/<slug:slug>/attachments', views.product_attachments, name='product_attachments_list'),
    path('products/<slug:slug>/attachments/new', views.new_product_attachment, name='new_product_attachment'),
    path('products/<slug:slug>/attachments/<int:id>/edit', views.edit_product_attachment, name='edit_product_attachment'),
]
