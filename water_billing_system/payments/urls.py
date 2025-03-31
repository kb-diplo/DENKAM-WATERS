from django.urls import path
from .views import (
    PaymentListView, 
    PaymentCreateView, 
    PaymentDetailView,
    PaymentUpdateView,
    PaymentDeleteView,
    generate_receipt
)

app_name = 'payments'

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('create/', PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('<int:pk>/update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment_delete'),
    path('<int:pk>/receipt/', generate_receipt, name='generate_receipt'),
]