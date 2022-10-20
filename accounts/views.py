import logging

from chat.models import Conversation
from helpers import DocxEditor
log = logging.getLogger(__name__)
from collections import namedtuple
import datetime as dt
from locale import currency
import os,string,json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.authtoken.models import Token
import random
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.conf import settings
from rest_framework import generics
from django.db.models import Q

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from .chatuser_serializer import UserSerializer as ChatUserSerializers
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
# import stripe
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.mailservice import Mailservice
from accounts.models import NDAAttachment, Quotes, ReportSeller, ResetPassword, UserJWTtokens, WishlistedProduct, Address, Review, NDA, NDAProposals, NDAPurchases, NDATransferHistory, NDAUser
from dashboard.transactions import RefundTransactions
from decorators import allowed_users, authorize_seller
from products.models import Product, Category, Variant, OptionType, OptionValue, Tag, Attachment
from accounts.models import User, CreditCard, UserProduct
from orders.models import Cart, CartItem, Order, LineItem, Transaction
from accounts.authentication import ( JWTAuthenticationMiddleWare, create_access_token, 
                                 create_refresh_token, decode_access_token, decode_refresh_token
                                 )
from endless_factory_api.serializers import AddressSerializer, GetAddressSerializer, IdCardAttachmentSerializer, NDAAttachmentSerializer, NDAPurchaseSerializer, ProofBusinessAttachmentSerializer, QuoteAttachmentSerializer, SellerCentreBasicInfoSerializer, SellerCentreBusinessInfoSerializer, TransactionsSerializer, UserProfileSerializer, UserSerializer, OrderAddressSerializer, VariantSerializer, VariantUpdateSerializer, UserShowSerializer, CreditCardSerializer , NDAProposalsSerializer, NDASerializer
from dotenv import load_dotenv
from tasks.__task__email import *
from django.db import transaction

load_dotenv()
refresh_jwt_token_life = int(os.getenv("REFRESH_JWT_TOKEN_LIFE"))
ISSUER_NAME = os.getenv("2FA_ISSUER_NAME")
DECLINE_REASONS = ('Shady Proposal','Has Previous Scam History','I am Uninterested')

def registration_otp(request):
    
    try:
        user = ResetPassword(email=request.data.get('email'))
       
        user.otp = random.randint(100000, 999999)
        print(user.otp)
        expiry_time = timezone.now() + timezone.timedelta(minutes=10)
        log.info(str(expiry_time))
        user.otp_expires_at = expiry_time
        user.reset_password_token = get_random_string(length=32)
        user.save()
        return {'status':True,'otp': user.otp, 'reset_password_token': user.reset_password_token}
    except:
        return {'status': False, 'message': 'Invalid Email'}

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()

class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()



class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False)
    def all(self, request):
        serializer = UserSerializer(
            User.objects.all(), many=True, context={"request": request}
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
class UsersView(APIView):
    # serializer_class = UserSerializer
    # queryset = User.objects.all()
    # authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self, request):
        serializer = UserSerializer(
            User.objects.all(), many=True
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    

      
class CustomObtainAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):

        user =request.data["email"]
        token, created = Token.objects.get_or_create(user=get_object_or_404(User,email=user))
        user = authenticate(request, email=user) or User.objects.filter(email=user).first()
        data = {}
        if user.is_verified_account == True:
            if user is not None:  
                def innerlogin():   
                    payload_object = {'id':user.id,'email':user.email,'seller_verified':user.biz_info_verified} # Add more data as needed
                    access_token = create_access_token(payload_object)   # Commented out for two factor Authentication
                    refresh_token = create_refresh_token(payload_object)
                    UserJWTtokens.objects.create(
                        user_id = user.id,
                        token = refresh_token,
                        expiredAt = dt.datetime.utcnow() + dt.timedelta(days=refresh_jwt_token_life)
                    )
                    response = Response()
                    response.set_cookie(key='refresh_token',value=refresh_token, samesite=None, httponly=True)
                    response.data = {"token": access_token, "email": user.email}
                    return response
                response = innerlogin()
                return response

            else:
                data['status'] = 'error'
                data['error'] = 'Invalid login credentials'
                return Response(data, status=200)
        
        else:
            data['status'] = 'error'
            data['error'] = 'Unverified user'
            return Response(data, status=200)

class RegisterView(APIView):
    def post(self,request):
        try:
            data = request.data
            response = {}
            if data['password'] != data['password_confirm']:
                return Response({'status':False,'message':'Passwords do not match'})
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                instance = serializer.save()
                cart = Cart.objects.create(token=get_random_string(length=32))
                instance.cart_token = cart.token
                instance.save()
                response['status'] = True
                response['email'] = instance.email
                response['cart_token'] = instance.cart_token
                
                otp_response = registration_otp(request)
                mail = {"otp":otp_response['otp'],
                        "subject":"Verify email account",
                        "sender":ISSUER_NAME,
                        "recipient":instance.email}
                send_email_task.delay(mail)
                response['temporary_otp_here'] = otp_response['otp']
                return Response(response)
            else:
                data = serializer.errors
                return Response({'status': False, 'errors': data})
        except Exception as e:
            return Response({'status': False, 'errors': f"An error {str(e)} occured during registration"})

class LoginView(APIView):
    def post(self,request):
        
        print(request.data)
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('user_type')
        request.session['session_key_clone'] = request.session.session_key
        user = authenticate(request, email=email) or User.objects.filter(email=email).first()
        data = {}
        try:
            if not user.check_password(password):
                return Response({'status':False,'message':'Invalids credentials supplied'})
            print("Verification status ",user.is_verified_account)
        except:
            return Response({'status':False,'message':'Invalids credentials supplied'})
        
        try:
            if user.is_verified_account == True:
                if user is not None:  
                    def innerlogin():   
                        payload_object = {'id':user.id,'email':user.email,'seller_verified':user.biz_info_verified} # Add more data as needed
                        access_token = create_access_token(payload_object)   # Commented out for two factor Authentication
                        refresh_token = create_refresh_token(payload_object)
                        UserJWTtokens.objects.create(
                            user_id = user.id,
                            token = refresh_token,
                            expiredAt = dt.datetime.utcnow() + dt.timedelta(days=refresh_jwt_token_life)
                        )
                        response = Response()
                        response.set_cookie(key='refresh_token',value=refresh_token, samesite=None, httponly=True)
                        response.data = {'status':True,'cart_token':user.cart_token,'jwt_token':access_token,'tfa_status':False}
                        return response
                    response = innerlogin()
                    return response
            
                else:
                    data['status'] = 'error'
                    data['error'] = 'Invalid login credentials'
                    return Response(data, status=200)

            else:
                return Response({"message":"User account has not been verified","status":False})
        
        except Exception as e:
            return Response({'status': False, 'errors': f"An error {str(e)} occured during login"})
        
class UserView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
      
class RequestOtpView(APIView):
    def post(self,request):
        instance = User.objects.filter(email=request.data.get('email')).first()
        reset_obj = ResetPassword.objects.get(email=request.data.get('email'))
        if reset_obj.email == request.data.get('email'):
            reset_obj.delete()
            print("exists already")
        if instance is not None:
            
            return Response(registration_otp(request))
        return Response({'status':False,'message':'User not found..'})

class RegistrationValidateOtpView(APIView):
    def post(self,request):
        try:
            user = ResetPassword.objects.get(email=request.data.get('email'))
            is_otp_valid = True#int(user.otp) == int(request.data.get('otp'))
            instance = User.objects.filter(email=request.data.get('email')).first()

            # if timezone.now() > user.otp_expires_at:
            #     return Response({'status': False, 'message': 'Expired token , request for new token'})
            
            if instance is not None and is_otp_valid == True:
                instance.is_verified_account = True
                instance.save()
            return Response({'status':  True if is_otp_valid else False, 'message': "OTP validated" if is_otp_valid else "Inavlid OTP"})
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Invalid reset password token'})

class ValidateOtpView(APIView):
    def data(self,request):
        try:
            user = ResetPassword.objects.get(reset_password_token=request.data.get('reset_password_token'))
            is_otp_valid = user.otp == int(request.data.get('otp'))
            return Response({'status':  True if is_otp_valid else False, 'reset_password_token': user.reset_password_token, 'message': "OTP validated" if is_otp_valid else "Inavlid OTP"})
        except:
            return Response({'status': False, 'message': 'Invalid or expired token'})

class LogoutView(APIView):
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserJWTtokens.objects.filter(token=refresh_token).delete()
        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {'status':True,'message':'Successfully logged out'}
        return response

class ForgotPasswordView(APIView):
    
    def post(self, request):
        
        reset_otp = random.randint(100000, 999999)
        reset_token = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50))
        try:
            reset_obj = ResetPassword.objects.get(email=request.data.get('email'))
    
            if reset_obj.email == request.data.get('email'):
                reset_obj.otp = reset_otp
                reset_obj.reset_password_token = reset_token
                reset_obj.save()
                mailservicedata = {}
                mailservicedata['otp'] = reset_otp
                mailservicedata['subject'] = "Password reset mail"
                mailservicedata['sender'] = ISSUER_NAME
                mailservicedata['recipient'] = request.data['email']
                send_password_reset_email_task.delay(mailservicedata,)
                return Response({'status':True,'message':f'Password reset otp was sent to {request.data["email"]}','temporary_otp':reset_otp})
            else:
                return Response({'status':False,'message':f'Our database does not know you'})
        
        except Exception as e:
            log.info(str(e))
            return Response({'status':False,'message':f'Our database does not know you'})
            

class ResetPasswordView(APIView):
    def post(self, request):
        data = request.data
        if data['password'] != data['password_confirm']:
            return Response({"status":False, "message":"Passwords do not match!"})
        reset_password_obj = ResetPassword.objects.filter(otp=data['otp']).first()
        
        if not reset_password_obj:
            return Response({"status":False, "message":"Invalid reset otp!"})
        
        user = User.objects.filter(email=reset_password_obj.email).first()
        
        if not user:
            return Response({"status":False, "message":"User not found!"})

        user.set_password(data['password'])
        user.save()
        ResetPassword.objects.filter(otp=data['otp']).delete()
        return Response({"status":True, "message":"Your password was successfully reset!"})


class AddressesView(generics.CreateAPIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        
        data = Address.objects.filter(user=request.user.id,deleted=False)
        serializer= GetAddressSerializer(data, many=True)
        return Response({'addresses': serializer.data})
    
    def post(self,request):
        
        if request.method == 'POST':
            request.data['user'] = request.user.id
            serializer= AddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # request.user.addresses.add(address)
                return Response({'address': serializer.data, "status": True})
            else:
                return Response({'message': serializer.errors, "status": False})
        

class PreferredAddressView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        address = Address.objects.filter(is_default_address=True,user=request.user.id,deleted=False).first()
        serializer= AddressSerializer(address, many=False)
        return Response({'preferred_address': serializer.data, "status": True})


class GetEditAddress(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request, pk):
        if request.method == 'GET':
            address = get_object_or_404(Address, pk=pk, deleted=False)
            serializer= AddressSerializer(address, many=False)
            return Response({'address': serializer.data, "status": True})
    
    def put(self,request,pk):
        if request.method == 'PUT':
            address = get_object_or_404(Address, pk=pk)
            data = request.data
            if data.get('is_default_address') == True:
                try:
                    reset = Address.objects.filter(user=request.user.id)
                    for addr in reset:
                        addr.is_default_address = False
                    reset.save()
                    previous_default = Address.objects.filter(is_default_address=True,user=request.user.id)
                    
                    if previous_default.is_default_address:
                        return Response({'message': 'User has default address already, contact admin for help', "status": False})
                except:
                    return Response({'message': 'User has more than one default address already, contact admin for help', "status": False})
                # if previous_default.is_default_address:
                #     previous_default.is_default_address = False
                #     previous_default.save()
                    
            serializer= AddressSerializer(address, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'address': serializer.data, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})
            
    def delete(self,request,pk):
        if request.method == 'DELETE':
            address = get_object_or_404(Address, pk=pk)
            if address.is_default_address:
                return Response({'message': 'Default address cannot be deleted', "status": False})
            address.deleted = True
            address.save()
            return Response({'message': 'Address deleted', "status": True})
           
class ChangePassword(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def post(self,request):
        try:
            user = User.objects.get(email=request.data.get('email'), password=request.data.get('current_password'))
            user.password = user.set_password(request.data.get('new_password'))
            user.save()
            return Response({'status': True,'message':"Password has been changed"})
        except:
            return Response({'status': False, 'message': 'Invalid current password'})
  
    
class UserProfile(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        serializer= UserShowSerializer(request.user, many=False)
        return Response({'user': serializer.data, "status": True})
    
    def put(self,request):
        if request.method == 'PUT':
            serializer= UserProfileSerializer(request.user, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                log.info(serializer.data)
                return Response({'user': serializer.data, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": False})


class CreditCardsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        credit_cards = CreditCard.objects.filter(user=request.user.id)
        serializer= CreditCardSerializer(credit_cards, many=True)
        return Response({'credit_cards': serializer.data})
    
    def post(self,request):
        if request.method == 'POST':
            request.data['user'] = request.user.id
            serializer= CreditCardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'credit_card': serializer.data, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})

class GetCreditCard(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request, pk):
        if request.method == 'GET':
            credit_card = get_object_or_404(CreditCard, pk=pk)
            serializer= CreditCardSerializer(credit_card, many=False)
            return Response({'credit_card': serializer.data})
        

class TransactionsView(APIView):

    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def validate_search_params(self,multi_param_obj):
        try:
            def validate_date(date_text):
                try:
                    datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
                    return True
                except ValueError:
                    return "Incorrect data format, should be YYYY-MM-DD"
                
            assert type(multi_param_obj.status) == str, 'Status should be a string'
            assert type(multi_param_obj.amount) == float, 'Amount should be a float value'
            assert type(multi_param_obj.currency) == str, 'Currency should be a string'
            assert multi_param_obj.currency.upper() in settings.CURRENCIES, 'Currency is invalid'
            assert validate_date(multi_param_obj.start_date) == True, 'Incorrect data format, should be YYYY-MM-DD'
            assert validate_date(multi_param_obj.end_date) == True, 'Incorrect data format, should be YYYY-MM-DD'
            return True
        
        except Exception as e:
            return str(e)
        
    def get(self,request):
        transactions = Transaction.objects.filter(customer= request.user.id)
        serializer= TransactionsSerializer(transactions, many=True)
        return Response({'status':True, 'transactions': serializer.data})
    
    def post(self,request):
        if request.method == 'POST':
            
            q = request.data.get('q')
            param = request.data.get('param') # Optional
            multi_param = request.data.get('params') # Optional
            
            if multi_param is not None:
                multi_param_obj = namedtuple("Queryparams", multi_param.keys())(*multi_param.values()) #Convert dict to object type
            
                try:
                    is_valid = self.validate_search_params(multi_param_obj)
                    if is_valid:
                        
                        assert 'accounts.views.Queryparams' in str(type(multi_param_obj))
                        print(multi_param_obj,type(multi_param_obj),multi_param_obj)
                        transactions = Transaction.objects.filter(customer= request.user.id,
                                                                    status=multi_param_obj.status,
                                                                    amount_paid=multi_param_obj.amount, 
                                                                    currency=multi_param_obj.currency.lower(),
                                                                    time_sent__range=[multi_param_obj.start_date,
                                                                    multi_param_obj.end_date]
                                                                    )
                        serializer= TransactionsSerializer(transactions, many=True)
                        return Response({'status':True, 'transactions': serializer.data})
                
                    if type(is_valid) == str:
                        return Response({'status':False, 'message': is_valid})
                except:
                    return Response({'status':False, 'message': is_valid})
             
            if q is None:
                transactions = Transaction.objects.filter(customer= request.user.id)
                serializer= TransactionsSerializer(transactions, many=True)
                return Response({'staus':True, 'transactions': serializer.data})
            
            elif q is not None and len(param)>=1:
                if param == "currency":
                    assert q.upper() in settings.CURRENCIES
                transactions = Transaction.objects.filter(customer= request.user.id, **{f'{param}__icontains': q})
                serializer= TransactionsSerializer(transactions, many=True)
                return Response({'status':True, 'transactions': serializer.data})


class TransactionsRefundView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def validate_search_params(self,multi_param_obj):

        try:
            def validate_date(date_text):
                try:
                    datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
                    return True
                except ValueError:
                    return "Incorrect data format, should be YYYY-MM-DD"
                
            assert type(multi_param_obj.status) == str, 'Status should be a string'
            assert type(multi_param_obj.amount) == float, 'Amount should be a float value'
            assert type(multi_param_obj.currency) == str, 'Currency should be a string'
            assert validate_date(multi_param_obj.start_date) == True, 'Incorrect data format, should be YYYY-MM-DD'
            assert validate_date(multi_param_obj.end_date) == True, 'Incorrect data format, should be YYYY-MM-DD'
            return True
        
        except Exception as e:
            return str(e)
        
    def post(self,request):
        if request.method == 'POST':
            data_obj = namedtuple("Queryparams", request.data.keys())(*request.data.values()) #Convert dict to object type
            try:
                is_valid = self.validate_search_params(data_obj)
                if is_valid:
                    limit = data_obj.limit
                    self.refundtransactions = RefundTransactions(charge_id='')
                    refunds = self.refundtransactions.list_refunds(request.user.id,data_obj,singlecharge=True,limit=limit)
                    return Response({'status':True, 'refunds': refunds})
            except:
                pass
        
#######################SETUP VERIFIED BUSINESS/SELLER'S ACCOUNT####################

class SellerCentreBasicInfo(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    @allowed_users()
    def post(self,request):
        
        if request.method == 'POST':
            request.data['user'] = request.user.id
            serializer= SellerCentreBasicInfoSerializer(request.user,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True,'message':"Seller Basic information was successfully submitted",'data': serializer.data})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})

class SellerCentreBusinessInfo(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    # @allowed_users()
    def post(self,request):
        
        with transaction.atomic():
            docs = ['id-document','pbo-document']
            if request.method == 'POST':
                try:
                    data = request.data['data']
                except Exception as e:
                    return Response({'errors': str(e), "status": False})
                
                if request.user.biz_info_submitted:
                    return Response({"status": False,'message':"Seller Business information was previously submitted"})
                
                request.data['user'] = request.user.id
                try:
                    serializer= SellerCentreBusinessInfoSerializer(request.user,data=json.loads(data))
                except:
                    return Response({'errors': serializer.errors,'message':'Invalid json format supplied', "status": False})
                
                if serializer.is_valid():
                    instance = serializer.save()
                    for doc in docs:
                        instance = self.saveAttachments(request,instance,json.loads(data),request.FILES.getlist(doc, None),doc)
                    if instance:
                        instance.biz_info_submitted = True
                        instance.save()
                        return Response({"status": True,'message':"Seller Business information was successfully submitted",'data': serializer.data})
                    else:
                        return Response({'errors': serializer.errors, "status": 'error'})
                else:
                    return Response({'errors': serializer.errors, "status": 'error'})
    
    
    def saveAttachments(self,request,instance,data,files,doc=''):
        
        if request.method == 'POST':
            data['user'] = str(instance.id)
            if doc == 'id-document':
                instance = IdCardAttachmentSerializer(data=data,context={'id-documents': files})
            elif doc == 'pbo-document':
                instance = ProofBusinessAttachmentSerializer(data=data,context={'pbo-documents': files})
            if instance.is_valid():
                return instance.create(data)


class QuotesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def post(self,request):
        with transaction.atomic():
            docs = ['quote-documents']
            if request.method == 'POST':
                try:
                    data = request.data['data']
                except Exception as e:
                    return Response({'errors': str(e), "status": False})
                request.data['user'] = request.user.id
                try:    
                    data=json.loads(data)
                    product = int(data.get('product'))
                    seller = UserProduct.objects.filter(product_id=product).values('user_id').first()
                    seller = get_object_or_404(User,id = seller['user_id'])
                    product = get_object_or_404(Product, id=product)

                    instance= Quotes.objects.create(customer=request.user.id,seller=seller,quote=data.get('quote'),product_fielded_by = product)
                    if instance:
                        self.continue_process(request,instance,data,docs)
                        return Response({'message':'Success creating quote', "status": True})
                    return Response({'errors': str(e),'message':'An error occured while creating quote', "status": False})
                except Exception as e:
                    print({'errors': str(e),'message':'An error occured while creating quote', "status": False})
                    return Response({'errors': str(e),'message':'An error occured while creating quote', "status": False})
            
    def continue_process(self,request,instance,data,docs):
        
        for doc in docs:
            instance = self.saveAttachments(request,instance,data,request.FILES.getlist(doc, None),doc)
            
        if instance:
            return Response({"status": True,'message':"Seller Business information was successfully submitted"})
        else:
            return Response({'errors': 'errors', "status": 'error'})
     
    def saveAttachments(self,request,instance,data,files,doc=''):
        
        if request.method == 'POST':
            data['quote'] = get_object_or_404(Quotes ,id=instance.id) 
            if doc == 'quote-documents':
                response = {'quote-documents': files,'data':data}
                print(response)
                instance = QuoteAttachmentSerializer(data=data,context={'quote-documents': files})
            if instance.is_valid():
                return instance.create(data)
            
            
class ReportSellerView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def post(self,request):
        
        if request.method == 'POST':
            try:
                data = request.data
                product = int(data.get('product'))
                seller = UserProduct.objects.filter(product_id=product).values('user_id').first()
                seller = get_object_or_404(User,id = seller['user_id'])
                ReportSeller.objects.create(customer=request.user.id,seller=seller,complaint=data.get('complaint'),radio_text=data.get('radio_text'))
                
                return Response({"status": True,'message':"Your complaint has been successfully submitted"})
            except:
                return Response({'errors': 'Your submission was not successful', "status": False})
        return Response({'errors': 'Unsupported request', "status": False})


class NDAUpload(APIView):
    
    def post(self,request):
        doc = 'nda-document'
        files = request.FILES.getlist(doc, None)
        with transaction.atomic():
            instance= NDA.objects.create()
            if instance:
                if request.method == 'POST':
                    if doc == 'nda-document':
                        for file in files:
                            instance_ = NDAAttachment.objects.create(nda_id=instance.id,file=file,attachment_type='document')
                            instance_.save()
                        return instance_

class NDAPricesView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        return Response({'status':True, 'nda_price_list': {'10':1000,'20':1900,'50':3500},
                         "message":"Fola this is a mock price list for now,where 10,20,50 are the number of NDA the person wants to buy and the values are the prices for each respectively"
                         })

class NDARegisterPurchaseView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def convert(self,tup, di):
        di = dict(tup)
        return di
    
    def get(self,request):
        nda_count = NDAUser.objects.filter(user_id=request.user.id).values('nda_count')
        return Response({'status':True,"nda_count":nda_count})

    def post(self,request):
        try:
            data = request.data
            data['nda_bought'] = NDA.objects.get(id=data['nda_bought']).id
            nda_user = NDAUser.objects.get_or_create(user=get_object_or_404(User,email=data.get('buyer')),nda_bought=int(data['nda_bought']))[0]
            data['nda_user'] = nda_user.id
            data.pop('buyer')
            instance = NDAPurchaseSerializer(data=data,many=False)
            
            if instance.is_valid():
                instance.save()
                dictionary = {}
                saved_vals = tuple(instance.data.items())
                parsed = self.convert(saved_vals, dictionary)
                nda_user.nda_count = int(data['amount'])
                nda_user.expires_at = parsed['expires_at']
                nda_user.save()
                
                return Response({'status':True,"message":f"This payment has been registered successfully and you have {nda_user.nda_count} NDA points"})
            return Response({'status':False,"message":"This payment could not be registered successfully"})
        except Exception as e:
            return Response({'status':False,"message":str(e)})
               
class NDAView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request):
        
        ndas = NDA.objects.get(id=4)
        serializer= NDASerializer(ndas)
        document = NDAAttachment.objects.get(nda_id=4)
        return Response({'status':True, 'nda_list': serializer.data,'document':str(document.file)})
     
    def post(self,request):
        
        if request.method == 'POST':
            try:
                data = request.data
                nda_from_user = NDAUser.objects.get_or_create(user=get_object_or_404(User,email=request.user.email))[0]
                status,message = self.check_action_and_nda_validity(nda_from_user)
                
                if status:
                    nda_to_user = NDAUser.objects.get_or_create(user=get_object_or_404(User,email=data.get('to_user')))[0]
                    nda_attachment = self.generate_nda_pdf(request,nda_from_user,data.get('to_user')) 
                    NDAProposals.objects.create(from_user=nda_from_user,to_user=nda_to_user,slug=nda_attachment)
                    nda_from_user.nda_count -= 1
                    nda_from_user.save()
                    return Response({"status": True,'nda_attachment':nda_attachment,'message':f"Your selected nda has been sent, you have {nda_from_user.nda_count} NDA's left which will expire on {nda_from_user.expires_at}"})
                else:
                    return Response({'message': message, "status": False})
                
            except Exception as e:
                return Response({'error':str(e),'msg': 'Your proposal submission was not successful', "status": False})
        return Response({'errors': 'Unsupported request', "status": False})

    def check_action_and_nda_validity(self,nda_from_user):
        
        if nda_from_user.nda_count < 1:
            return False, 'You do not have any NDA left to send, please purchase more NDA'
        elif timezone.now() >= nda_from_user.expires_at:
            return False, 'Your NDA has expired, please purchase new NDA'
        else:
            return True,'NDA sufficient and valid'
            
    def generate_nda_pdf(self,request,nda_from_user,recepient):
        path = NDA.objects.get(id=nda_from_user.nda_bought).nda_attachment()[0]
        nda_template_path = f"/var/www/endless_factory_api/media_root/{path}"
        self.docx_editor = DocxEditor(request.user.name,get_object_or_404(User,email=recepient).name)
        return self.docx_editor.convert_docx_to_pdf(nda_template_path).replace('/var/www/endless_factory_api/media_root/','http://165.232.185.232:8000/api/v1')
        
        
class NDAProposalsView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    
    def get(self,request):
        proposal_user = request.user.email
        pending_ndas = request.GET.get('pending') or ''
        nda_user = NDAUser.objects.get_or_create(user=get_object_or_404(User,email=proposal_user))[0]
        lookups =  Q(to_user_id=nda_user.id) if pending_ndas.lower() == 'true' else Q(to_user_id=nda_user.id)
        proposals = NDAProposals.objects.filter(lookups)#.values()
        serializer= NDAProposalsSerializer(proposals, many=True)
            
        return Response({'status':True, 'proposals_list': serializer.data,"decline_reason_options":DECLINE_REASONS})
    
    def put(self,request): 
        action = request.data.get('action')
        decline_reason = request.data.get('decline_reason')
        proposal_id = int(request.data.get('proposal_id'))
        if request.method == 'PUT':
            try:
                proposal = get_object_or_404(NDAProposals,id=proposal_id)
                if action == 'accept' or action == 'decline':
                    proposal.status = action.title()
                else:
                     return Response({'errors': 'Unsupported action', "status": False})
                if action.lower() == 'decline':
                    if decline_reason not in DECLINE_REASONS:
                        return Response({'message': 'You must provide a valid reason for declining', "status": False})
                    proposal.decline_reason = decline_reason
                proposal.save()
                # sendmail()
                return Response({"status": True,'message':f"This proposal has been {action}"})
            except:
                return Response({'errors': 'Your action on this proposal was not successful', "status": False})
        return Response({'errors': 'Unsupported request', "status": False})
    
# # class NDATransferView(APIView):
    
# #     authentication_classes = [JWTAuthenticationMiddleWare]

# #     def post(self,request):
        
# #         if request.method == 'POST':
# #             try:
# #                 data = request.data
# #                 amount = int(data['amount'])
# #                 nda_id = int(data.get('nda'))
# #                 nda_from_user = get_object_or_404(NDAUser,user= get_object_or_404(User,email=data.get('from_user')))
# #                 nda_to_user = get_object_or_404(NDAUser,user= get_object_or_404(User,email=data.get('to_user')))
# #                 nda = NDA.objects.get(id=nda_id)
# #                 status,message = self.send_nda(nda,nda_from_user,nda_to_user,amount)
# #                 return Response(message)
# #             except:
# #                 return Response({'errors': 'Your proposal submission was not successful', "status": False})
# #         return Response({'errors': 'Unsupported request', "status": False})
    
# #     def check_action_and_nda_validity(self,nda_from_user):
        
# #         if nda_from_user.nda_count < 1:
# #             return False, 'You do not have any NDA left to send, please purchase more NDA'
        
# #         elif timezone.now() >= nda_from_user.expires_at:
# #             return False, 'Your Current NDA points has expired, please purchase new NDA Points'
        
# #         else:
# #             True,'NDA sufficient and valid'
            
# #     def send_nda(self,nda,nda_from_user,nda_to_user,amount):
        
# #         status,message = self.check_action_and_nda_validity(nda_from_user)
# #         if status:
# #             #Send the NDA points here
# #             with transaction.atomic():
# #                 nda_from_user.nda_count -= amount
# #                 saved = nda_from_user.save()
# #                 if saved:
# #                     nda_to_user.count += amount
# #                     nda_to_user.save()
# #                     NDATransferHistory.objects.create(nda_from_user=nda_from_user,nda_to_user=nda_to_user,nda=nda,amount=amount)
# #                     return status, {'message':f'You have sent {amount} NDA Points to {nda_to_user}, you have {nda_from_user.nda_count} NDA points left'}
# #         else:
# #             return status,message
        
# class NDAPurchaseView(APIView):
    
#     authentication_classes = [JWTAuthenticationMiddleWare]
    
#     def post(self,request):
        
#         if request.method == 'POST':
#             data = request.data
#             with transaction.atomic():
#                 nda_user = NDAUser.objects.get_or_create(user= get_object_or_404(User,email=data.get('email')))
#                 nda_bought = NDA.objects.get(id=data['nda_id'])
#                 transaction_ref = data['transaction_ref']
#                 amount = int(data['amount'])
#                 price = float(data['price'])
#                 instance = NDAPurchases.objects.create(nda_user=nda_user,nda_bought=nda_bought,transacton_ref=transaction_ref,amount=amount,price=price)
#                 nda_user.expires_at = instance.expires_at
#                 nda_user.save()
          