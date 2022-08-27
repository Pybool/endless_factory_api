from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from orders.models import Cart
from .forms import CreatUserForm
from django.contrib import messages
from django.utils.crypto import get_random_string

from products.models import Category
from accounts.models import User


def loginPage(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    if request.user.is_authenticated:
        messages.success(request, 'User already logged in.')

        return redirect('/dashboards/home')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password) or User.objects.filter(email=email, password=password).first()

            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in Successfully.')
                return redirect('/dashboards/home')
            else:
                messages.error(request, 'Email or Password is incorrect.')
        context = {'categories': product_categories,'lang': get_user_locale(request)}
        return render(request, 'accounts/login.html', context)

def forgot_password(request):
    if request.user.is_authenticated:
        messages.success(request, 'User already logged in.')

        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()

            if user is not None:
                user.otp = 123456
                user.reset_password_token = get_random_string(length=32)
                user.save()
                messages.success(request, 'OTP sent over mail')
                return redirect('validate_otp', user.reset_password_token)
            else:
                messages.error(request, 'User with email does not exists')
                return redirect('login')
    product_categories = Category.objects.all().order_by('?')[:8]
    context={'categories': product_categories, 'lang': get_user_locale(request)}    
    return render(request, 'accounts/forgot_password.html', context)

def reset_password(request, token):
    product_categories = Category.objects.all().order_by('?')[:8]
    user_with_token =  User.objects.filter(reset_password_token = token).first()
    if request.user.is_authenticated:
        messages.success(request, 'User already logged in.')
        return redirect('/')
    elif user_with_token is None:
        messages.error(request, 'Invalid reset password token')
        return redirect('login')
    else:
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirmation = request.POST.get('password_confirmation')
            if password == password_confirmation:
                user_with_token.password = password
                user_with_token.otp = None
                user_with_token.reset_password_token = None
                user_with_token.save()
                messages.success(request, 'Password changed successfully')
                return redirect('login')
            else:
                messages.error(request, 'Passwords should match')
                return redirect('reset_password', token)
    context = {'categories': product_categories, 'lang': get_user_locale(request)}
    return render(request, 'accounts/reset_password.html', context)

def validate_otp(request, token):
    product_categories = Category.objects.all().order_by('?')[:8]
    user_with_token =  User.objects.filter(reset_password_token = token).first()
    if request.user.is_authenticated:
        messages.success(request, 'User already logged in.')
        return redirect('/')
    elif user_with_token is None:
        messages.error(request, 'Invalid reset password token')
        return redirect('login')
    else:
        if request.method == 'POST':
            otp = request.POST.get('otp')
            user = User.objects.filter(reset_password_token = token, otp=otp).first()

            if user is not None:
                return redirect('reset_password', user.reset_password_token)
            else:
                messages.error(request, 'Invalid OTP')
                return redirect('validate_otp', token)
    context={'categories': product_categories,'lang': get_user_locale(request)}
    return render(request, 'accounts/validate_otp.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


def registerPage(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    if request.user.is_authenticated:
        return redirect('/dashboards/home')
    else:
        form = CreatUserForm()
        if request.method == 'POST':
            form = CreatUserForm(request.POST)
            if form.is_valid():
                form.save()
                cart = Cart.objects.create(token=get_random_string(length=32))
                user_object = form.instance
                user_object.cart_token = cart.token
                user_object.save()

                messages.success(request, 'You have registered successfully!')
                return redirect('/')
        context = {'form': form, 'categories': product_categories, 'lang': get_user_locale(request)}
        return render(request, 'accounts/register.html', context)

def get_user_locale(request):
    try:
        return request.COOKIES['locale']
    except:
        return 'en'