from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from billing.models import Bill
from payments.models import Payment
from meter_readings.models import MeterReading
from django.db import models

logger = logging.getLogger(__name__)

@csrf_exempt
def custom_permission_denied_view(request, exception):
    logger.warning(f'Permission denied: {request.path} - {exception}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    return render(request, '403.html', status=403)

@csrf_exempt
def custom_page_not_found_view(request, exception):
    logger.warning(f'Page not found: {request.path} - {exception}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Page not found'}, status=404)
    return render(request, '404.html', status=404)

@csrf_exempt
def custom_error_view(request):
    logger.error(f'Server error: {request.path}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Server error'}, status=500)
    return render(request, '500.html', status=500)

@login_required
def dashboard(request):
    context = {}
    user = request.user

    if user.role in ['admin', 'supplier']:
        # Admin/Supplier Dashboard Data
        context.update({
            'customer_count': Customer.objects.count(),
            'paid_bills_count': Bill.objects.filter(status='paid').count(),
            'pending_bills_count': Bill.objects.filter(status='pending').count(),
            'overdue_bills_count': Bill.objects.filter(status='overdue').count(),
            'recent_readings': MeterReading.objects.select_related('customer', 'meter').order_by('-reading_date')[:5],
            'recent_payments': Payment.objects.select_related('customer').order_by('-payment_date')[:5],
        })

    elif user.role == 'meter_reader':
        # Meter Reader Dashboard Data
        today = timezone.now().date()
        context.update({
            'scheduled_readings': MeterReading.objects.filter(
                reading_date__date=today,
                reader=user
            ).select_related('customer', 'meter').order_by('reading_date')
        })

    elif user.role == 'customer':
        # Customer Dashboard Data
        customer = user.customer
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get current month's usage
        latest_reading = MeterReading.objects.filter(
            customer=customer,
            reading_date__gte=current_month_start
        ).order_by('-reading_date').first()

        previous_reading = MeterReading.objects.filter(
            customer=customer,
            reading_date__lt=current_month_start
        ).order_by('-reading_date').first()

        current_month_usage = 0
        if latest_reading and previous_reading:
            current_month_usage = latest_reading.reading_value - previous_reading.reading_value

        context.update({
            'current_month_usage': current_month_usage,
            'outstanding_balance': Bill.objects.filter(
                customer=customer,
                status__in=['pending', 'overdue']
            ).aggregate(total=models.Sum('amount'))['total'] or 0,
            'last_payment': Payment.objects.filter(customer=customer).order_by('-payment_date').first(),
            'recent_bills': Bill.objects.filter(customer=customer).order_by('-billing_period')[:5],
            'recent_payments': Payment.objects.filter(customer=customer).order_by('-payment_date')[:5],
        })

    return render(request, 'dashboard.html', context)