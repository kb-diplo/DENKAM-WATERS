"""
URL configuration for water_billing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from customers.views import home  
from meter_readings import views as meter_views
from customers import views as customer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('meter-readings/', include('meter_readings.urls')),
    path('customers/', include('customers.urls')),
    path('', home, name='home'),  
    path('', include('customers.urls')),
    path('meter-readings/', include('meter_readings.urls')),
    path('meter-readings/add/', meter_views.add_meter_reading, name='add_meter_reading'),
    path('meter-readings/success/', meter_views.meter_reading_success, name='meter_reading_success'),
    path('customers/', customer_views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', customer_views.customer_detail, name='customer_detail'),
]