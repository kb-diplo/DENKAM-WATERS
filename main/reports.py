from django.db.models import Sum, Count, F
from .models import WaterBill, Client, MeterReading
from datetime import date, timedelta

def generate_billing_report(start_date, end_date):
    return {
        'total_bills': WaterBill.objects.filter(
            created_at__date__range=(start_date, end_date)
        ).count(),
        'total_revenue': WaterBill.objects.filter(
            created_at__date__range=(start_date, end_date)
        ).aggregate(Sum('payable'))['payable__sum'] or 0,
        'unpaid_bills': WaterBill.objects.filter(
            status='Pending',
            created_at__date__range=(start_date, end_date)
        ).count(),
    }

def generate_consumption_report(start_date, end_date):
    return MeterReading.objects.filter(
        reading_date__range=(start_date, end_date)
    ).values(
        'client__name'
    ).annotate(
        total_consumption=Sum('reading_value'),
        bill_count=Count('water_bill')
    ).order_by('-total_consumption')