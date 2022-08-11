from django.http import HttpResponse
from django.shortcuts import redirect
from dashboard import views
from django.contrib import messages

def unnauthenticate_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboards/home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def allowed_users():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_buyer():
                messages.error(request, 'You are not authorized to view this page.')
                return redirect('frontend_home')
            else:
                return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator

def authorize_seller():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_admin():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You are not authorized to view this page.')
                return redirect('dashboard_home')
        return wrapper_func
    return decorator
