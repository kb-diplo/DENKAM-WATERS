from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/<int:pk>/', views.receipt_detail, name='receipt_detail'),
    path('receipts/<int:pk>/pdf/', views.receipt_pdf, name='receipt_pdf'),
    path('customer/<int:customer_id>/', views.customer_payments, name='customer_payments'),
]