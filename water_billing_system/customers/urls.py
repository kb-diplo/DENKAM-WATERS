from django.urls import path
from . import views

urlpatterns = [
    # Home page for customers
    path('', views.customer_dashboard, name='customer_dashboard'),

    # Billing history
    path('billing-history/', views.billing_history, name='billing_history'),

    # Payment history
    path('payment-history/', views.payment_history, name='payment_history'),

    # Account management
    path('account/', views.account_management, name='account_management'),

    # Update account details
    path('account/update/', views.update_account, name='update_account'),

    # Water usage tracking
    path('usage/', views.water_usage, name='water_usage'),
]