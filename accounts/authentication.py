from datetime import datetime
import os, jwt, datetime
from django.utils.crypto import get_random_string
from orders.models import Cart
from .models import User
from dotenv import load_dotenv
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
load_dotenv()
algorithm = str(os.getenv("JWT_ALGORITHM"))
jwt_token_life = int(os.getenv("JWT_TOKEN_LIFE"))
jwt_token_secret_key = str(os.getenv("JWT_TOKEN_SECRET_KEY"))
refresh_jwt_token_life = int(os.getenv("REFRESH_JWT_TOKEN_LIFE"))

def get_authorization_token(request,auth):
        auth = get_authorization_header(request).split()
        
        if auth and len(auth)==2:
            print(auth)
            return auth[1].decode('utf-8')
        if auth is True:
            raise exceptions.AuthenticationFailed('Unauthenticated')
        return False
    
# Authentication MIDDLEWARE CLASS 
class JWTAuthenticationMiddleWare(BaseAuthentication):
        
    def authenticate(self,request,auth=True):
        
        token = get_authorization_token(request,auth)
        id = decode_access_token(token)
        print(id)
        user = User.objects.get(pk=id)
        print("\n\n\nCurrent user ",user)
        return (user, None)
        
        
def create_access_token(payload_object):
    
    return jwt.encode({
        'user_id':payload_object['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=jwt_token_life),
        'iat':datetime.datetime.utcnow()
    },jwt_token_secret_key,algorithm=algorithm)
    
def decode_access_token(token,cart=False):
    try:
        if cart is False:
            print(token)
            payload = jwt.decode(token,jwt_token_secret_key,algorithms=algorithm)
            print(payload)
            return payload['user_id']
        return jwt.decode(token,jwt_token_secret_key,algorithms=algorithm)['cart_token']
    except Exception as e:
        if cart is False:
            raise exceptions.AuthenticationFailed('Unauthenticated user')
        else:
            cart_token= Cart.objects.create(token=get_random_string(length=32)).token
            return create_access_token({"id":cart_token,"cart_token":cart_token}),cart_token
    
def create_refresh_token(payload_object):
    
    return jwt.encode({
        'user_id':payload_object['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=refresh_jwt_token_life),
        'iat':datetime.datetime.utcnow()
    },jwt_token_secret_key,algorithm=algorithm)

def decode_refresh_token(token):
    try:
        payload = jwt.decode(token,jwt_token_secret_key,algorithms=algorithm)
        return payload['user_id']
    except Exception as e:
        raise exceptions.AuthenticationFailed('Unauthenticated user')