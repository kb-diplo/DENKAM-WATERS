from django.urls import path
from .views import (
    landingpage, dashboard, meter_reader_dashboard, client_dashboard, ongoing_bills, history_bills, update_bills, delete_bills, profile, 
    users, add_as_client, update_user, delete_user, register_customer, clients, client_update, client_delete, metrics, metricsupdate, meter_reading, 
    client_bill_history, manage_billing, reports, initiate_mpesa_payment, mpesa_callback, add_bill, get_previous_reading, record_payment,
    admin_password_change, record_meter_reading, get_bill_details
)

app_name = 'main'

urlpatterns = [
    path('', landingpage, name='landingpage'),
    path('dashboard/', dashboard, name='dashboard'),
    path('meter-reader/dashboard/', meter_reader_dashboard, name='meter_reader_dashboard'),
    path('client/dashboard/', client_dashboard, name='client_dashboard'),

    path('profile/<int:pk>/', profile, name='profile'),
    path('admin/password/change/', admin_password_change, name='admin_password_change'),

    path('users/', users, name='users'),
    path('user/add/', register_customer, name='register_customer'),
    path('user/update/<int:pk>/', update_user, name='update_user'),
    path('user/delete/<int:pk>/', delete_user, name='delete_user'),

    path('clients/', clients, name='clients'),
    path('client/add_as_client/<int:pk>/', add_as_client, name='add_as_client'),
    path('client/update/<int:pk>/', client_update, name='client_update'),
    path('client/delete/<int:pk>/', client_delete, name='client_delete'),

    path('bills/ongoing/', ongoing_bills, name='ongoing_bills'),
    path('bills/history/', history_bills, name='history_bills'),
    path('bill/add/', add_bill, name='add_bill'),
    path('bill/update/<int:pk>/', update_bills, name='update_bills'),
    path('bill/delete/<int:pk>/', delete_bills, name='delete_bills'),
    path('api/get-previous-reading/', get_previous_reading, name='get_previous_reading'),
    path('api/get-bill-details/', get_bill_details, name='get_bill_details'),

    path('meter-reading/', meter_reading, name='meter_reading'),
    # API endpoint for recording meter readings
    path('api/record-meter-reading/', record_meter_reading, name='record_meter_reading'),
    path('billing/manage/<int:pk>/', manage_billing, name='manage_billing'),

    path('metrics/', metrics, name='metrics'),
    path('metrics/update/<int:pk>/', metricsupdate, name='metrics_update'),

    path('reports/', reports, name='reports'),
    path('record-payment/', record_payment, name='record_payment'),

    path('my-billing-history/', client_bill_history, name='client_bill_history'),
    path('pay-with-mpesa/<int:bill_id>/', initiate_mpesa_payment, name='initiate_mpesa_payment'),
    path('mpesa-callback/', mpesa_callback, name='mpesa_callback'),
]
