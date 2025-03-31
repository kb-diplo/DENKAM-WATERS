from django.urls import path
from .views import (
    MeterReadingListView, 
    MeterReadingCreateView, 
    MeterReadingDetailView,
    MeterReadingUpdateView,
    MeterReadingDeleteView
)

app_name = 'meter_readings'

urlpatterns = [
    path('', MeterReadingListView.as_view(), name='reading_list'),
    path('create/', MeterReadingCreateView.as_view(), name='reading_create'),
    path('<int:pk>/', MeterReadingDetailView.as_view(), name='reading_detail'),
    path('<int:pk>/update/', MeterReadingUpdateView.as_view(), name='reading_update'),
    path('<int:pk>/delete/', MeterReadingDeleteView.as_view(), name='reading_delete'),
]