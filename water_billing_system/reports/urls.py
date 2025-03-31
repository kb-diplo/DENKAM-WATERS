from django.urls import path
from .views import (
    ReportListView,
    SalesReportView,
    PaymentsReportView,
    BalancesReportView,
    generate_report_pdf
)

app_name = 'reports'

urlpatterns = [
    path('', ReportListView.as_view(), name='report_list'),
    path('sales/', SalesReportView.as_view(), name='sales_report'),
    path('payments/', PaymentsReportView.as_view(), name='payments_report'),
    path('balances/', BalancesReportView.as_view(), name='balances_report'),
    path('<int:pk>/pdf/', generate_report_pdf, name='generate_report_pdf'),
]