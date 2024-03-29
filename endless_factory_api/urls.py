"""endless_factory_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from chat.consumer import ChatConsumer
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# from conversa_dj.users.api.views import CustomObtainAuthTokenView


urlpatterns = [
    
    path('admin/', include('admin_accounts.urls')),
    path('', include('frontend.urls')),
    path("", include("config.api_router")),
    path('', include('marketing.urls')),
    path('', include('admin_dashboard.urls')),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('dashboard.urls')),
    path('api/v1/', include('products.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('order_tracking.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('chat.urls')),
    path('dashboards/', include('admin_dashboard.urls')),
    path('careers/', include('careers.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 