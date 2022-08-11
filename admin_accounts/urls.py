from django.urls import path

from admin_accounts import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('<str:token>/validate_otp', views.validate_otp, name='validate_otp'),
    path('<str:token>/reset_password', views.reset_password, name='reset_password'),
]
