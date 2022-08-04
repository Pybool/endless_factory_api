from collections import namedtuple
import datetime as dt
from locale import currency
import os,string,json
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
import random
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.conf import settings
from rest_framework import generics
from django.conf import settings
# import stripe
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.mailservice import Mailservice
from accounts.models import ResetPassword, UserJWTtokens, WishlistedProduct, Address, Review
from dashboard.transactions import RefundTransactions
from decorators import allowed_users, authorize_seller
from products.models import Product, Category, Variant, OptionType, OptionValue, Tag, Attachment
from accounts.models import User, CreditCard, UserProduct
from orders.models import Cart, CartItem, Order, LineItem, Transaction
from accounts.authentication import ( JWTAuthenticationMiddleWare, create_access_token, 
                                 create_refresh_token, decode_access_token, decode_refresh_token
                                 )
from endless_factory_api.serializers import IdCardAttachmentSerializer, ProofBusinessAttachmentSerializer, SellerCentreBasicInfoSerializer, SellerCentreBusinessInfoSerializer, TransactionsSerializer, UserSerializer, AddressSerializer, VariantSerializer, VariantUpdateSerializer, UserShowSerializer, CreditCardSerializer
from dotenv import load_dotenv
from tasks.__task__email import *
load_dotenv()
refresh_jwt_token_life = int(os.getenv("REFRESH_JWT_TOKEN_LIFE"))

ISSUER_NAME = os.getenv("2FA_ISSUER_NAME")


def registration_otp(request):
    
    try:
        user = ResetPassword(email=request.data.get('email'))
       
        user.otp = random.randint(100000, 999999)
        print(user.otp)
        expiry_time = timezone.now() + timezone.timedelta(minutes=1)
        print("expiry time ", expiry_time)
        user.otp_expires_at = expiry_time
        user.reset_password_token = get_random_string(length=32)
        user.save()
        return {'status':True,'otp': user.otp, 'reset_password_token': user.reset_password_token}
    except:
        return {'status': False, 'message': 'Invalid Email'}


class RegisterView(APIView):
    def post(self,request):
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

class LoginView(APIView):
    def post(self,request):
        print(request.data)
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('user_type')
        user = authenticate(request, email=email) or User.objects.filter(email=email, user_type=user_type).first()
        data = {}
        
        if not user.check_password(password):
            return Response({'status':False,'message':'Invalids credentials supplied'})
        print("Verification status ",user.is_verified_account)
        if user.is_verified_account == True:
            if user is not None:  
                def innerlogin():   
                    payload_object = {'id':user.id,'email':user.email} # Add more data as needed
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
        
class UserView(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
      
class RequestOtpView(APIView):
    def post(self,request):
        instance = User.objects.filter(email=request.data.get('email')).first()
        reset_obj = ResetPassword.objects.get(email=request.data.get('email'))
        print("Existing ",reset_obj.email)
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
            is_otp_valid = int(user.otp) == int(request.data.get('otp'))
            instance = User.objects.filter(email=request.data.get('email')).first()

            if timezone.now() > user.otp_expires_at:
                return Response({'status': False, 'message': 'Expired token , request for new token'})
            
            if instance is not None and is_otp_valid == True:
                instance.is_verified_account = True
                # instance.otp_expires_at = timezone.now()
                instance.save()
                user.delete()
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
            print("Existing ",reset_obj.email)
            if reset_obj.email == request.data.get('email'):
                reset_obj.otp = reset_otp
                reset_obj.reset_password_token = reset_token
                reset_obj.save()
        
        except:
            ResetPassword.objects.create(
                otp = reset_otp,
                email = request.data['email'],
                reset_password_token = reset_token
            )
        # url = f"http:localhost:3000/confirmreset/{reset_token}" #MOVE THE BASE URL TO SETTINGS.PY
        mailservicedata = {}
        mailservicedata['otp'] = reset_otp
        mailservicedata['subject'] = "Password reset mail"
        mailservicedata['sender'] = ISSUER_NAME
        mailservicedata['recipient'] = request.data['email']
        send_password_reset_email_task.delay(mailservicedata,)
        return Response({'status':True,'message':f'Password reset otp was sent to {request.data["email"]}','temporary_otp':reset_otp})
    
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
        
        data = Address.objects.filter(user=request.user.id)
        serializer= AddressSerializer(data, many=True)
        return Response({'addresses': serializer.data})
    
    def post(self,request):
        
        if request.method == 'POST':
            request.data['user'] = request.user.id
            serializer= AddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # request.user.addresses.add(address)
                return Response({'address': serializer.data, "status": 'ok'})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})
        

class PreferredAddressView(APIView):
    
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request):
        address = Address.objects.filter(is_shipping_address=True,user=request.user.id).first()
        serializer= AddressSerializer(address, many=False)
        return Response({'preferred_address': serializer.data, "status": True})


class GetEditAddress(APIView):
    authentication_classes = [JWTAuthenticationMiddleWare]
    def get(self,request, pk):
        if request.method == 'GET':
            address = get_object_or_404(Address, pk=pk)
            serializer= AddressSerializer(address, many=False)
            return Response({'address': serializer.data, "status": True})
    
    def put(self,request,pk):
        if request.method == 'PUT':
            address = get_object_or_404(Address, pk=pk)
            serializer= AddressSerializer(address, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'address': serializer.data, "status": True})
            else:
                return Response({'errors': serializer.errors, "status": 'error'})

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
    
    def post(self,request):
        if request.method == 'POST':
            serializer= UserShowSerializer(request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
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
                    refunds = self.refundtransactions.list_refunds('2' or request.user.id,data_obj,singlecharge=True,limit=limit)
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
    @allowed_users()
    def post(self,request):
        docs = ['id-document','pbo-document']
        if request.method == 'POST':
            
            if request.user.biz_info_submitted:
                return Response({"status": False,'message':"Seller Business information was previously submitted"})
            
            request.data['user'] = request.user.id
            serializer= SellerCentreBusinessInfoSerializer(request.user,data=json.loads(request.data['data']))
            if serializer.is_valid():
                instance = serializer.save()
                for doc in docs:
                    instance = self.saveAttachments(request,instance,json.loads(request.data['data']),request.FILES.getlist(doc, None),doc)
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
            print("Files ",files,doc)
            data['user'] = str(instance.id)
            if doc == 'id-document':
                instance = IdCardAttachmentSerializer(data=data,context={'id-documents': files})
            elif doc == 'pbo-document':
                instance = ProofBusinessAttachmentSerializer(data=data,context={'pbo-documents': files})
            if instance.is_valid():
                return instance.create(data)
