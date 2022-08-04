from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
from .import views

urlpatterns = [
  path('user/signup', views.RegisterView.as_view()),
  path('user/signin', views.LoginView.as_view()),
  path('user/signout',views.LogoutView.as_view()),
  
  path('user/signup_verify_otp', views.RegistrationValidateOtpView.as_view()),
  path('user/request_otp', views.RequestOtpView.as_view()),
  path('forgot_password/send_reset_token', views.ForgotPasswordView.as_view()),
  path('forgot_password/reset_password', views.ResetPasswordView.as_view()),

  path('user/set_addresses', views.AddressesView.as_view()),
  # path('user/wishlisted_products', views.wishlistedproducts),
  path('user/get_edit_addresses/<int:pk>', views.GetEditAddress.as_view()),
  
  path('user/credit_cards', views.CreditCardsView.as_view()),
  path('user/credit_cards/<int:pk>', views.GetCreditCard.as_view()),
  path('user/preferred-address', views.PreferredAddressView.as_view()),

  path('user/profile', views.UserProfile.as_view()),
  path('user/change_password', views.ChangePassword.as_view()),
  
  
  path('account/sellercentre_basic_info', views.SellerCentreBasicInfo.as_view()),
  path('account/sellercentre_business_info', views.SellerCentreBusinessInfo.as_view()),
  
  
  path('user/get_transactions', views.TransactionsView.as_view()),
  path('user/get_transaction/refunds', views.TransactionsRefundView.as_view()),
  

  
  
  # path('user/wishlisted_products/add_product', views.mark_product_wishlisted),
  # path('user/wishlisted_products/remove_product', views.mark_product_unwishlisted),

  
]
