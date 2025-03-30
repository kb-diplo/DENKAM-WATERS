from django.urls import path
from . import views

urlpatterns = [
    path('input/', views.add_meter_reading, name='add_meter_reading'),
    path('success/', views.meter_reading_success, name='meter_reading_success'),
 ]