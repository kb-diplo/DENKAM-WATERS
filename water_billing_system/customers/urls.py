from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    path('meters/', views.MeterListView.as_view(), name='meter_list'),
    path('meters/create/', views.MeterCreateView.as_view(), name='meter_create'),
    path('meters/<int:pk>/edit/', views.MeterUpdateView.as_view(), name='meter_edit'),
    path('meters/<int:pk>/delete/', views.MeterDeleteView.as_view(), name='meter_delete'),
]