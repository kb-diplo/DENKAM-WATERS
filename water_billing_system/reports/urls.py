from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('billing/', views.billing_report, name='billing_report'),
    path('billing/pdf/', views.billing_report_pdf, name='billing_report_pdf'),
    path('payments/', views.payments_report, name='payments_report'),
    path('payments/pdf/', views.payments_report_pdf, name='payments_report_pdf'),
    path('consumption/', views.consumption_report, name='consumption_report'),
    path('consumption/pdf/', views.consumption_report_pdf, name='consumption_report_pdf'),
    path('customers/', views.customers_report, name='customers_report'),
    path('customers/pdf/', views.customers_report_pdf, name='customers_report_pdf'),
]