from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.http import HttpRequest
import logging

from chat.views import ConversationsViewSet
log = logging.getLogger(__name__)
from chat.consumer import ChatConsumer
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
  
  path('user/contact_seller/request_quote', views.QuotesView.as_view()),
  path('user/report_seller', views.ReportSellerView.as_view()),
  
  path('auth-token/', views.CustomObtainAuthTokenView.as_view()),
  path('users/all/', views.UsersView.as_view()),
  path('uploadnda/', views.NDAUpload.as_view()),
  path('nda/', views.NDAView.as_view()),
  path('get_nda/pricelist', views.NDAPricesView.as_view()),
  path('nda/register_purchase', views.NDARegisterPurchaseView.as_view()),
  path('nda/proposals/', views.NDAProposalsView.as_view()),
  
  
  
  # path("conversations/<chat_id>/", ConversationsViewSet),
 ]