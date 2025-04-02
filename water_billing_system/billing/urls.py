from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.bill_create, name='bill_create'),
    path('<int:pk>/', views.bill_detail, name='bill_detail'),
    path('<int:pk>/update/', views.bill_update, name='bill_update'),
    path('<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('<int:pk>/pdf/', views.bill_pdf, name='bill_pdf'),
    path('<int:pk>/mark-paid/', views.bill_mark_paid, name='bill_mark_paid'),
    path('tariffs/', views.tariff_list, name='tariff_list'),
    path('tariffs/create/', views.tariff_create, name='tariff_create'),
    path('tariffs/<int:pk>/edit/', views.tariff_edit, name='tariff_edit'),
    path('tariffs/<int:pk>/delete/', views.tariff_delete, name='tariff_delete'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
]