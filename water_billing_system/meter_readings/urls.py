from django.urls import path
from . import views

app_name = 'meter_readings'

urlpatterns = [
    path('', views.MeterReadingListView.as_view(), name='reading_list'),
    path('create/', views.MeterReadingCreateView.as_view(), name='reading_create'),
    path('<int:pk>/', views.MeterReadingDetailView.as_view(), name='reading_detail'),
    path('<int:pk>/edit/', views.MeterReadingUpdateView.as_view(), name='reading_edit'),
    path('<int:pk>/delete/', views.MeterReadingDeleteView.as_view(), name='reading_delete'),
    path('customer/<int:customer_id>/', views.customer_readings, name='customer_readings'),
    path('meter/<int:meter_id>/', views.meter_readings, name='meter_readings'),
]