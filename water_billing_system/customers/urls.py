from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('meters/', views.meter_list, name='meter_list'),
    path('meters/create/', views.meter_create, name='meter_create'),
    path('meters/<int:pk>/edit/', views.meter_edit, name='meter_edit'),
    path('meters/<int:pk>/delete/', views.meter_delete, name='meter_delete'),
]