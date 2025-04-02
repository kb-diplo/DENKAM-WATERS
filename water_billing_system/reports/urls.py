from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('payments/', views.PaymentsReportView.as_view(), name='payments_report'),
    path('balances/', views.BalancesReportView.as_view(), name='balances_report'),
    path('report/<int:pk>/pdf/', views.generate_report_pdf, name='report_pdf'),
]