from django.urls import path
from . import views

urlpatterns = [
    path('input/', views.input_meter_reading, name='input_meter_reading'),
]