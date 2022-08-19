from django.http import HttpResponse
from rest_framework.response import Response
from django.shortcuts import redirect
# from dashboard import views
from django.contrib import messages

def unnauthenticate_user(view_func):
    def wrapper_func(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboards/home')
        else:
            return view_func(self,request, *args, **kwargs)

    return wrapper_func

def allowed_users():
    def decorator(view_func):
        def wrapper_func(self,request, *args, **kwargs):
            if request.user.is_buyer():
                msg = {'status':False,'message':'You are not authorized to view this page.'}
                # return Response(msg)
                return view_func(self,request, *args, **kwargs)
            
            elif request.user.is_seller():
                if request.user.is_info_verified() is False:
                    msg = {'status':False,'message':'You are not authorized to view this page, your seller account is not verified yet.'}
                    return Response(msg)
                else:
                    return view_func(self,request, *args, **kwargs)
            else:
                return view_func(self,request, *args, **kwargs)
        return wrapper_func
    return decorator

def authorize_seller():
    def decorator(view_func):
        def wrapper_func(self,request, *args, **kwargs):
            if request.user.is_admin():
                return view_func(self,request, *args, **kwargs)
            else:
                msg = {'status':False,'message':'You are not authorized to view this page.'}
                return Response(msg)
        return wrapper_func
    return decorator
