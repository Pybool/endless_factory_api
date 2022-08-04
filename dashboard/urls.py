from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('dashboard/home', views.HomeView.as_view()),
  path('dashboard/profile', views.ProfileView.as_view()),
  path('dashboard/newuser', views.NewUserView.as_view()),
  path('dashboard/edituser/<int:pk>', views.EditUserView.as_view()),
  path('dashboard/allusers', views.UsersView.as_view()),
  path('dashboard/allusers/wishlist_products', views.AllUsersWishlistedProductsView.as_view()),
  path('dashboard/singleuser/addresses/<int:pk>', views.SingleUsersAddressesView.as_view()),
  path('dashboard/singleuser/new_addresses/<int:pk>', views.NewUsersAddressesView.as_view()),
  path('dashboard/singleuser/edit_addresses/<int:pk>/<int:address_id>', views.EditUsersAddressesView.as_view()),
  path('dashboard/singleuser/credit_cards/<int:pk>', views.SingleUsersCreditCardsView.as_view()),
  
  path('dashboard/new_option_type', views.NewOptionTypeView.as_view()),
  path('dashboard/new_option_value', views.NewOptionValueView.as_view()),

  path('dashboard/new_category', views.NewCategoriesView.as_view()),
  path('dashboard/product_tags', views.TagsView.as_view()),
  path('dashboard/product_tags/<slug:slug>', views.TagsView.as_view()),
  path('dashboard/new_product', views.NewProductsView.as_view()),
  path('dashboard/products', views.ProductsView.as_view()),
  path('dashboard/orders', views.SellerHomeData.as_view()),
  path('dashboard/search_orders/<search_string>', views.OrdersSearch.as_view()),
  path('dashboard/orders/mark_shipped', views.MarkItemsShipped.as_view()),
  path('dashboard/sales_dashboard/statistics/<filter>/<int:duration>', views.SellerDashboardView.as_view()),
  path('dashboard/verification/sellers/<int:pk>', views.VerifySellerBusinessView.as_view()),
  
  path('dashboard/marketing/new_campaign', views.NewCampaignView.as_view()),

  
  
  
  
 ]
