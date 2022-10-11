from logging import exception
from urllib.parse import parse_qs
import os, jwt, datetime
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from dotenv import load_dotenv
load_dotenv()
algorithm = str(os.getenv("JWT_ALGORITHM"))
jwt_token_life = int(os.getenv("JWT_TOKEN_LIFE"))
jwt_token_secret_key = str(os.getenv("JWT_TOKEN_SECRET_KEY"))
refresh_jwt_token_life = int(os.getenv("REFRESH_JWT_TOKEN_LIFE"))
import logging
log = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        # log.info(str("user ===> ")+str(user_id))
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class WebSocketJWTAuthMiddleware:

    def __init__(self, app):
        self.app = app
        # log.info(app)

    def decode_access_token(self,token):
        try:
            print(token)
            # log.info(str("user ===> ")+str(token))
            payload = jwt.decode(token,jwt_token_secret_key,algorithms=algorithm)
            # log.info(payload)
            return payload
        except Exception as e:
            raise exception.AuthenticationFailed('Unauthenticated user')
        
    async def __call__(self, scope, receive, send):
        parsed_query_string = parse_qs(scope["query_string"])
        token = parsed_query_string.get(b"token")[0].decode("utf-8")

        try:
            access_token = self.decode_access_token(token)
            scope["user"] = await get_user(access_token["user_id"])
            
        except Exception as e:
            scope["user"] = AnonymousUser()

        # log.info(scope["user"])
        return await self.app(scope, receive, send)
    
    
    