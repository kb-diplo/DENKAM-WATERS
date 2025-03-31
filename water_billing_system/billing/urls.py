from django.urls import path
from .views import (
    BillListView, 
    BillCreateView, 
    BillDetailView,
    BillUpdateView,
    BillDeleteView,
    TariffListView,
    TariffCreateView,
    TariffUpdateView,
    TariffDeleteView,
    generate_invoice
)

app_name = 'billing'

urlpatterns = [
    path('', BillListView.as_view(), name='bill_list'),
    path('create/', BillCreateView.as_view(), name='bill_create'),
    path('<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
    path('<int:pk>/update/', BillUpdateView.as_view(), name='bill_update'),
    path('<int:pk>/delete/', BillDeleteView.as_view(), name='bill_delete'),
    path('<int:pk>/invoice/', generate_invoice, name='generate_invoice'),
    
    path('tariffs/', TariffListView.as_view(), name='tariff_list'),
    path('tariffs/create/', TariffCreateView.as_view(), name='tariff_create'),
    path('tariffs/<int:pk>/update/', TariffUpdateView.as_view(), name='tariff_update'),
    path('tariffs/<int:pk>/delete/', TariffDeleteView.as_view(), name='tariff_delete'),
]