from django.urls import path
from . import views

app_name = 'meter_readings'

urlpatterns = [
    path('', views.reading_list, name='reading_list'),
    path('create/', views.reading_create, name='reading_create'),
    path('<int:pk>/', views.reading_detail, name='reading_detail'),
    path('<int:pk>/edit/', views.reading_edit, name='reading_edit'),
    path('<int:pk>/delete/', views.reading_delete, name='reading_delete'),
    path('customer/<int:customer_id>/', views.customer_readings, name='customer_readings'),
    path('meter/<int:meter_id>/', views.meter_readings, name='meter_readings'),
]