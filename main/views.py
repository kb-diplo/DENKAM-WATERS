from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_http_methods
from django.db.models import Max, Q, F, Sum, Count
from django.db.models.functions import Coalesce, TruncMonth
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import datetime
from decimal import Decimal
from .forms import BillForm, ClientUpdateForm, ClientForm, MetricsForm, MeterReadingForm, AddBillForm, PaymentRecordForm
from account.models import *
from .forms import *
from account.forms import UpdateUserForm
from mpesa.models import MpesaPayment
from .mpesa_utils import initiate_stk_push
from django.db.models import F, Sum
import sweetify
import json
from account.forms import MeterReaderClientCreationForm
from account.decorators import admin_required, customer_or_admin_required, customer_required, admin_or_meter_reader_required, meter_reader_required
from .decorators import client_facing_login_required
from django.db import models, transaction
from django.utils import timezone
from collections import defaultdict
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def landingpage(request):
    return render(request, 'account/landingpage.html')  


@login_required(login_url='login')
@admin_required
def dashboard(request):
    # Get counts for different bill statuses
    paid_bills_count = WaterBill.objects.filter(status='Paid').count()
    pending_bills_count = WaterBill.objects.filter(status='Pending').count()
    overdue_bills_count = WaterBill.objects.filter(status='Overdue').count()
    meter_readers_count = Account.objects.filter(role='METER_READER').count()
    
    # Get metric rates
    metric = Metric.objects.first()
    consump_rate = metric.consumption_rate if metric else Decimal('1.0')
    penalty_rate = metric.penalty_rate if metric else Decimal('0.0')

    # Calculate total revenue from paid bills
    total_revenue = WaterBill.objects.filter(status='Paid').aggregate(
        total=Sum(F('meter_consumption') * consump_rate)
    )['total'] or Decimal('0.0')

    # Calculate outstanding payments from pending bills
    outstanding_payments = WaterBill.objects.filter(status='Pending').aggregate(
        total=Sum(F('meter_consumption') * consump_rate)
    )['total'] or Decimal('0.0')

    # Add penalties for overdue bills
    total_overdue_penalties = WaterBill.objects.filter(status='Overdue').aggregate(
        total_penalty=Sum('penalty')
    )['total_penalty'] or Decimal('0.0')
    
    outstanding_payments += total_overdue_penalties

    billing_data = {
        'paid': paid_bills_count,
        'pending': pending_bills_count,
        'overdue': overdue_bills_count,
    }

    context = {
        'title': 'Dashboard',
        'clients': Client.objects.all().count(),
        'bills': WaterBill.objects.all().count(),
        'ongoingbills': WaterBill.objects.filter(status='Pending'),
        'connecteds': Client.objects.filter(status='Connected').count(),
        'disconnecteds': Client.objects.filter(status='Disconnected').count(),
        'paid_bills_count': paid_bills_count,
        'pending_bills_count': pending_bills_count,
        'overdue_bills_count': overdue_bills_count,
        'billing_data': billing_data,
        'meter_readers_count': meter_readers_count,
        'total_revenue': total_revenue,
        'outstanding_payments': outstanding_payments,
    }
    return render(request, 'main/dashboard.html', context)


import logging
from django.conf import settings
logger = logging.getLogger(__name__)

@login_required(login_url='account:login')
@meter_reader_required
def meter_reader_dashboard(request):
    try:
        # Get current month and year for filtering
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Get search query if it exists
        search_query = request.GET.get('search', '').strip()
        
        # Get all clients with search filtering
        clients = Client.objects.select_related('name').order_by('name__first_name', 'name__last_name')
        
        # Apply search filter if query exists
        if search_query:
            clients = clients.filter(
                Q(name__first_name__icontains=search_query) |
                Q(name__last_name__icontains=search_query) |
                Q(meter_number__icontains=search_query) |
                Q(contact_number__icontains=search_query) |
                Q(name__email__icontains=search_query)
            )
        
        total_clients_count = clients.count()
        
        # Get billed clients for current month (only for the filtered clients if search is active)
        # First get all client IDs that have been billed this month with a reading > 0
        billed_this_month = WaterBill.objects.filter(
            name__in=clients,
            created_at__year=current_year,
            created_at__month=current_month,
            reading__gt=0  # Only consider bills with actual readings
        ).values_list('name_id', flat=True).distinct()
        
        # Convert to a set for faster lookups
        billed_client_ids = set(billed_this_month)
        
        # Get the count of billed clients
        billed_clients_count = len(billed_client_ids)
        
        # Calculate pending clients by excluding billed clients from the total
        pending_clients = clients.exclude(id__in=billed_client_ids)
        pending_clients_count = pending_clients.count()
        
        # For the client list, we need to know which clients are billed
        # So we'll keep billed_client_ids as a list for the template
        
        # Handle AJAX search requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = []
            for client in clients:
                # Get the last bill for this client in the current month
                current_month_bill = WaterBill.objects.filter(
                    name=client,
                    created_at__year=current_year,
                    created_at__month=current_month,
                    reading__gt=0  # Only consider bills with actual readings
                ).first()
                
                # Check if client is billed (has a bill with reading > 0 for current month)
                is_billed = current_month_bill is not None
                
                data.append({
                    'id': client.id,
                    'name': client.name.get_full_name() or client.name.email,
                    'meter_number': client.meter_number or 'N/A',
                    'contact_number': client.contact_number or 'N/A',
                    'is_billed': is_billed,
                    'url': reverse('main:manage_billing', args=[client.id])
                })
            # Return the data as a JSON object with a 'results' key
            return JsonResponse({'results': data}, safe=False)
        
        # Get the last reading for each client
        client_ids = [client.id for client in clients]
        last_readings = {}
        
        # Get the most recent reading for each client from WaterBill model
        latest_bills = WaterBill.objects.filter(
            name_id__in=client_ids,
            reading__isnull=False
        ).values('name_id').annotate(
            latest_reading=Max('reading'),
            latest_date=Max('created_at')
        )
        
        # Create a dictionary of client_id to last_reading
        for bill in latest_bills:
            client_id = bill['name_id']
            last_readings[client_id] = bill['latest_reading']
        
        # Add last_reading to each client object
        for client in clients:
            client.last_reading = last_readings.get(client.id, 0)  # Default to 0 if no reading found
        
        # Prepare context for regular page load
        context = {
            'title': 'Meter Reader Dashboard',
            'clients': clients,
            'search_query': search_query,
            'total_clients_count': total_clients_count,
            'billed_clients_count': billed_clients_count,
            'pending_clients_count': pending_clients_count,
            'billed_client_ids': billed_client_ids,
            'current_month': current_month,
            'current_year': current_year,
            'debug': settings.DEBUG,
        }
        
        # Log basic info for debugging
        if settings.DEBUG:
            print(f"Rendering dashboard for {request.user.email}")
            print(f"Found {total_clients_count} clients")
            print(f"Billed this month: {billed_clients_count}")
            print(f"Pending: {pending_clients_count}")
            if search_query:
                print(f"Search query: {search_query}")
        
        return render(request, 'main/meter_reader_dashboard.html', context)
        
    except Exception as e:
        error_msg = f"Error in meter_reader_dashboard: {str(e)}"
        if settings.DEBUG:
            print(error_msg)
            import traceback
            traceback.print_exc()
        
        # Handle AJAX errors
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'An error occurred while searching'}, status=500)
            
        sweetify.error(request, 'An error occurred while loading the dashboard.')
        return redirect('main:dashboard')


@login_required(login_url='account:login')
@customer_required
def client_dashboard(request):
    # Ensure the user has a client profile using the correct related_name
    if not hasattr(request.user, 'client_profile'):
        sweetify.error(request, 'No client profile found. Please contact support.')
        return redirect('account:login')
    
    client = request.user.client_profile
    
    # Get the client's bills, ordered by most recent
    client_bills = WaterBill.objects.filter(
        name=client
    ).select_related('name').order_by('-created_at')
    
    # Get counts for dashboard metrics
    unpaid_bills_count = client_bills.filter(status='Pending').count()
    paid_bills_count = client_bills.filter(status='Paid').count()
    
    # Get the most recent bill if it exists
    latest_bill = client_bills.first()
    
    context = {
        'title': 'My Dashboard',
        'client': client,
        'latest_bill': latest_bill,
        'unpaid_bills_count': unpaid_bills_count,
        'paid_bills_count': paid_bills_count,
    }
    return render(request, 'main/client_dashboard.html', context)

@login_required(login_url='account:login')
@customer_or_admin_required
def ongoing_bills(request):
    if request.user.role == Account.Role.ADMIN:
        ongoing_bills = WaterBill.objects.filter(status='Pending')
    else:
        # For customers, filter bills by their client profile
        try:
            client = request.user.client_profile
            ongoing_bills = WaterBill.objects.filter(name=client, status='Pending')
        except AttributeError:
            # If user doesn't have a client profile, return empty queryset
            ongoing_bills = WaterBill.objects.none()

    context = {
        'title': 'Ongoing Bills',
        'ongoingbills': ongoing_bills,
    }

    return render(request, 'main/billsongoing.html', context)


@login_required(login_url='account:login')
@customer_or_admin_required
def history_bills(request):
    if request.user.role == Account.Role.ADMIN:
        # Show all bills that are fully paid
        bills_history = WaterBill.objects.filter(
            status='Paid'
        ).order_by('-created_at')
    else:
        # For customers, filter bills by their client profile
        try:
            client = request.user.client_profile
            bills_history = WaterBill.objects.filter(
                name=client, 
                status='Paid'
            ).order_by('-created_at')
        except AttributeError:
            # If user doesn't have a client profile, return empty queryset
            bills_history = WaterBill.objects.none()

    context = {
        'title': 'Bills History',
        'billshistory': bills_history,
    }
    return render(request, 'main/billshistory.html', context)

@login_required(login_url='account:login')
@admin_required
def update_bills(request, pk):
    bill = get_object_or_404(WaterBill, id=pk)
    form = BillForm(instance=bill)
    context = {
        'title': 'Update Bill',
        'bill': bill,
        'form': form,
    }
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            # Save the form first
            updated_bill = form.save(commit=False)
            
            # Handle the client_name field if it's provided
            client_name = form.cleaned_data.get('client_name')
            if client_name and client_name != str(bill.name):
                # If the client name has changed, we need to handle this
                # For now, we'll just keep the existing client but show a message
                # In a more complex implementation, we might want to:
                # 1. Find an existing client with this name
                # 2. Create a new client if one doesn't exist
                # 3. Update the bill's client association
                pass
            
            updated_bill.save()
            sweetify.toast(request, f'{bill} updated successfully.')
            return HttpResponseRedirect(reverse('main:ongoing_bills'))
    return render(request, 'main/billupdate.html', context)


@login_required(login_url='login')
@admin_required
def delete_bills(request, pk):
    bill = get_object_or_404(WaterBill, id=pk)
    context = {
        'title': 'Delete Bill',
        'bill': bill,
    }
    if request.method == 'POST':
        bill.delete()
        sweetify.toast(request, f'{bill} deleted successfully.')
        return HttpResponseRedirect(reverse('main:ongoing_bills'))
    return render(request, 'main/billdelete.html', context)



@login_required
@login_required
def admin_password_change(request):
    """
    View for admin to change their password.
    """
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Basic validation
        if not all([current_password, new_password1, new_password2]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('main:admin_password_change')
            
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('main:admin_password_change')
            
        # Verify current password
        user = request.user
        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('main:admin_password_change')
            
        # Validate new password strength (Django's default validators will be used)
        if len(new_password1) < 8 or not any(char.isdigit() for char in new_password1) or not any(char.isalpha() for char in new_password1):
            messages.error(request, 'Password must be at least 8 characters long and contain both letters and numbers.')
            return redirect('main:admin_password_change')
            
        # All validations passed, update password
        user.set_password(new_password1)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Your password has been updated successfully!')
        return redirect('main:admin_password_change')
    
    return render(request, 'main/admin_password_change.html')


def profile(request, pk):
    """
    View for users to update their profile information and password.
    """
    # Ensure users can only view their own profile, unless they are an admin
    if not request.user.is_superuser and request.user.id != int(pk):
        sweetify.error(request, "You are not authorized to view this profile.")
        if request.user.role == 'CUSTOMER':
            return redirect('main:client_dashboard')
        elif request.user.role == 'METER_READER':
            return redirect('main:meter_reader_dashboard')
        else:
            return redirect('main:dashboard')

    user_account = get_object_or_404(Account, id=pk)
    client_instance = None
    
    # Try to get client instance if it exists
    if hasattr(user_account, 'client_profile'):
        client_instance = user_account.client_profile
    
    if request.method == 'POST':
        account_form = UpdateProfileForm(request.POST, instance=user_account, prefix='account')
        
        # Only process client form if user is a client or admin is editing
        client_form = None
        if client_instance or request.user.is_superuser:
            if request.user.is_superuser:
                client_form = ClientForm(request.POST, instance=client_instance, prefix='client') if client_instance else None
            else:
                client_form = ClientUpdateForm(request.POST, instance=client_instance, prefix='client') if client_instance else None
        
        # Check form validity
        forms_are_valid = account_form.is_valid()
        if client_form:
            forms_are_valid = forms_are_valid and client_form.is_valid()
        
        if forms_are_valid:
            # Save account info and update password if needed
            user = account_form.save(commit=False)
            
            # Check if password is being changed
            new_password = account_form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Important to keep user logged in
            
            user.save()
            
            # Save client info if form exists
            if client_form:
                client_form.save()
            
            sweetify.success(request, 'Profile updated successfully!')
            return redirect('main:profile', pk=user_account.id)
        else:
            sweetify.error(request, 'Please correct the errors below.')
    else:
        # Initialize forms for GET request
        account_form = UpdateProfileForm(instance=user_account, prefix='account')
        
        # Only show client form if user is a client or admin is viewing
        client_form = None
        if client_instance or request.user.is_superuser:
            if request.user.is_superuser:
                client_form = ClientForm(instance=client_instance, prefix='client') if client_instance else None
            else:
                client_form = ClientUpdateForm(instance=client_instance, prefix='client') if client_instance else None

    context = {
        'title': 'Profile',
        'account_form': account_form,
        'client_form': client_form,
        'profile': user_account,
        'is_client': client_instance is not None
    }
    return render(request, 'main/profile.html', context)

@login_required(login_url='login')
@admin_required
def users(request):
    # Get all non-admin users who are meter readers
    meter_readers = Account.objects.filter(is_superuser=False, role=Account.Role.METER_READER)
    clients = Account.objects.filter(is_superuser=False, role=Account.Role.CUSTOMER)

    context = {
        'title': 'Users',
        'meter_readers': meter_readers,
        'clients': clients,
    }
    return render(request, 'main/users.html', context)


@login_required(login_url='login')
@admin_required
@require_POST
def add_as_client(request, pk):
    user = get_object_or_404(Account, id=pk)
    if user.role == 'METER_READER':
        sweetify.error(request, 'A Meter Reader cannot be registered as a Client.')
        return redirect('users')
    if not Client.objects.filter(name=user).exists():
        Client.objects.create(name=user, contact_number='N/A', address='N/A')
        sweetify.success(request, f'{user.first_name} {user.last_name} has been added as a client.')
    else:
        sweetify.warning(request, f'{user.first_name} {user.last_name} is already a client.')
    return redirect('users')


@login_required(login_url='login')
@admin_required
def update_user(request, pk):
    user = get_object_or_404(Account, id=pk)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            sweetify.success(request, f'{user} updated successfully')
            return HttpResponseRedirect(reverse('main:users'))
        else:
            # Form is not valid, show errors
            sweetify.error(request, 'Please correct the errors below.')
    else:
        form = UpdateUserForm(instance=user)
    
    context = {
        'title': 'Users',
        'user': user,
        'form': form,
    }
    return render(request, 'main/userupdate.html', context)

@login_required(login_url='login')
@admin_required
def delete_user(request, pk):
    try:
        user = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        sweetify.error(request, 'User not found.')
        return HttpResponseRedirect(reverse('main:users'))
    
    context = {
        'title': 'Users',
        'user': user,
    }
    if request.method == 'POST':
        user.delete()
        sweetify.success(request, 'User deleted successfully.')
        return HttpResponseRedirect(reverse('main:users'))
    return render(request, 'main/userdelete.html', context)

@login_required(login_url='account:login')
@admin_required
def clients(request):
    # Handle CSV export
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="clients.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Meter Number', 'First Name', 'Last Name', 'Email', 'Contact Number', 'Address', 'Status', 'Created At'])
        
        clients = Client.objects.select_related('name').all()
        for client in clients:
            writer.writerow([
                client.id,
                client.meter_number,
                client.name.first_name if client.name else '',
                client.name.last_name if client.name else '',
                client.name.email if client.name else '',
                client.contact_number,
                client.address,
                client.status,
                client.created_at.strftime('%Y-%m-%d %H:%M:%S') if client.created_at else ''
            ])
        
        return response
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                client = form.save()
                sweetify.success(
                    request,
                    'New client has been added successfully!',
                    text=f'Login credentials have been sent to {client.name.email}.'
                )
                return redirect('main:clients')
            except Exception as e:
                sweetify.error(
                    request,
                    'Error creating client',
                    text=str(e),
                    persistent=True
                )
        else:
            sweetify.error(
                request,
                'Please correct the errors below',
                persistent=True
            )
    else:
        form = ClientForm()

    # Get all clients with their associated user accounts
    all_clients = Client.objects.select_related('name').all()
    
    context = {
        'title': 'Clients',
        'clients': all_clients,
        'form': form
    }
    return render(request, 'main/clients.html', context)

@login_required(login_url='login')
@admin_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    context = {
        'title': 'Delete Client',
        'client': client,
    }
    if request.method == 'POST':
        # The associated user account should also be deleted or handled appropriately
        # For example, if the client is linked to an Account via a OneToOneField named 'user_account'
        if hasattr(client, 'name') and client.name:
            client.name.delete() # This assumes 'name' is the related user account
        client.delete()
        sweetify.success(request, 'Client deleted successfully!')
        return redirect('clients')
    
    return render(request, 'main/clientdelete.html', context)


@login_required(login_url='login')
@admin_required
def client_billing_history(request, pk):
    client = get_object_or_404(Client, id=pk)
    bills = WaterBill.objects.filter(name=client).order_by('-created_at')
    context = {
        'title': f'Billing History - {client.first_name} {client.last_name}',
        'client': client,
        'bills': bills
    }
    return render(request, 'main/client_billing_history.html', context)

@login_required(login_url='login')
@admin_or_meter_reader_required
def client_update(request,pk):
    context = {
        'title': 'Update Client',
        'client': client,
        'form': form
    }
    return render(request, 'main/clientupdate.html', context)



def metrics(request):
    if not Metric.objects.all():
        Metric.objects.create()
    context = {
        'title': 'Metrics',
        'amount': Metric.objects.get(id=1)
    }
    return render(request, 'main/metrics.html', context)



def metricsupdate(request, pk):
    metrics = Metric.objects.get(id=pk)
    form = MetricsForm(instance=metrics)
    context = {
        'title': 'Update Metrics',
        'form': form
    }
    if request.method == 'POST':
        form = MetricsForm(request.POST, instance=metrics)
        if form.is_valid():
            form.save()
            sweetify.toast(request, 'Metrics updated successfully')
            return HttpResponseRedirect(reverse('main:metrics'))
    return render(request, 'main/metricsupdate.html', context)

@login_required(login_url='login')
@admin_or_meter_reader_required
def meter_reading(request):
    clients = Client.objects.select_related('name').all()
    query = request.GET.get('q')
    if query:
        clients = clients.filter(
            Q(name__first_name__icontains=query) |
            Q(name__last_name__icontains=query) |
            Q(name__email__icontains=query) |
            Q(meter_number__icontains=query) |
            Q(contact_number__icontains=query)
        ).distinct()

    paginator = Paginator(clients, 10)  # Show 10 clients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get billed client IDs for the current month
    now = timezone.now()
    billed_client_ids = WaterBill.objects.filter(
        created_at__year=now.year,
        created_at__month=now.month,
        name__in=clients
    ).values_list('name_id', flat=True)

    context = {
        'title': 'Meter Reading - Select Client',
        'page_obj': page_obj,
        'query': query,
        'billed_client_ids': list(billed_client_ids),
        'clients': clients  # Add clients to context for the template
    }
    return render(request, 'main/meter_reading.html', context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def client_bill_history(request, pk=None):
    # If pk is provided (admin viewing a specific client)
    if pk:
        client = get_object_or_404(Client, id=pk)
    # If no pk, use the logged-in user's client profile
    else:
        if not hasattr(request.user, 'client_profile'):
            sweetify.error(request, 'No client profile found. Please contact support.')
            return redirect('account:login')
        client = request.user.client_profile
    
    # Get the client's bills, ordered by most recent
    bills_list = WaterBill.objects.filter(name=client).order_by('-created_at')
    
    # Pagination - 10 items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(bills_list, 10)  # Show 10 bills per page
    
    try:
        bills = paginator.page(page)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)
    
    context = {
        'title': 'My Billing History' if not pk else f'Billing History for {client.name.get_full_name()}',
        'bills': bills,
        'client': client,
        'is_client_view': not bool(pk),  # Flag to indicate if this is the client's own view
        'page_obj': bills,  # For pagination controls
        'is_paginated': paginator.num_pages > 1  # Show pagination if more than 1 page
    }
    
    return render(request, 'main/client_bill_history.html', context)


@login_required(login_url='account:login')
@admin_or_meter_reader_required
def add_meter_reading(request, client_id):
    # Get the client and ensure they exist
    client = get_object_or_404(Client, id=client_id)
    
    # If user is a meter reader, verify they are assigned to this client
    if request.user.role == 'METER_READER' and client.assigned_meter_reader != request.user:
        sweetify.error(request, 'You are not authorized to add readings for this client.', persistent='OK')
        return redirect('meter_reader_dashboard')
    
    now = timezone.now()
    last_bill = WaterBill.objects.filter(name=client).order_by('-created_at').first()
    last_reading = last_bill.reading if last_bill else 0

    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            reading = form.cleaned_data['reading']

            if reading < last_reading:
                sweetify.error(request, 
                    f'New reading cannot be less than the previous reading of {last_reading}.')
                return render(request, 'main/add_meter_reading.html', {
                    'form': form,
                    'client': client,
                    'last_reading': last_reading,
                    'title': f'Add Meter Reading - {client.get_full_name()}'
                })
            
            try:
                consumption = reading - last_reading
                notes = form.cleaned_data.get('notes', '')
                
                # Create the bill first
                bill = WaterBill.objects.create(
                    name=client,
                    reading=reading,
                    meter_consumption=consumption,
                    created_by=request.user,
                    status='Pending',
                    duedate=now.date() + datetime.timedelta(days=15),
                    penaltydate=now.date() + datetime.timedelta(days=30),
                    notes=notes  # Save notes to the bill
                )
                
                # Create a meter reading record
                MeterReading.objects.create(
                    client=client,
                    reading_value=reading,
                    reading_date=now,
                    recorded_by=request.user,
                    bill=bill,
                    notes=notes  # Also save notes to the meter reading
                )
                
                sweetify.success(request, 'New meter reading has been recorded successfully!', persistent='OK')
                
                # Redirect based on user role
                if request.user.role == 'ADMIN':
                    return redirect('clients')
                else:
                    return redirect('meter_reader_dashboard')
                    
            except Exception as e:
                sweetify.error(request, f'Error recording meter reading: {str(e)}', persistent='OK')
        else:
            sweetify.error(request, 'Please correct the errors below.', persistent='OK')
    else:
        form = MeterReadingForm(initial={'reading': last_reading})

    context = {
        'form': form,
        'client': client,
        'title': f'Add Meter Reading for {client.first_name} {client.last_name}',
        'last_reading': last_reading
    }
    return render(request, 'main/add_meter_reading.html', context)


@login_required(login_url='login')
@admin_or_meter_reader_required
def add_bill(request):
    """
    View for adding a new bill with customer selection and auto-fill of previous reading.
    """
    if request.method == 'POST':
        form = AddBillForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            current_reading = form.cleaned_data['current_reading']
            
            # Get the previous bill for this client
            previous_bill = WaterBill.objects.filter(client=client).order_by('-created_at').first()
            previous_reading = previous_bill.meter_reading.reading_value if (previous_bill and hasattr(previous_bill, 'meter_reading')) else 0
            
            # Validate current reading is not less than previous reading
            if current_reading < previous_reading:
                sweetify.error(
                    request, 
                    f'Current reading ({current_reading}) cannot be less than the previous reading ({previous_reading}).',
                    persistent='OK'
                )
                return render(request, 'main/add_bill.html', {'form': form, 'title': 'Add New Bill'})
            
            # Calculate consumption
            consumption = current_reading - previous_reading
            
            # Create new meter reading
            meter_reading = MeterReading.objects.create(
                reading_value=current_reading,
                reading_date=timezone.now(),
                client=client,
                created_by=request.user
            )
            
            # Create new bill
            bill = WaterBill.objects.create(
                client=client,
                meter_reading=meter_reading,
                consumption=consumption,
                status='Pending',
                due_date=timezone.now().date() + timezone.timedelta(days=30),  # 30 days from now
                created_by=request.user
            )
            
            sweetify.success(
                request,
                f'Bill for {client.name.get_full_name()} created successfully!',
                persistent='OK'
            )
            return redirect('main:ongoing_bills')
    else:
        form = AddBillForm()
    
    return render(request, 'main/add_bill.html', {
        'form': form,
        'title': 'Add New Bill'
    })


def get_previous_reading(request):
    """
    API endpoint to get the previous reading for a client.
    Used for auto-filling the previous reading field.
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        client_id = request.GET.get('client_id')
        try:
            client = Client.objects.get(id=client_id)
            last_bill = WaterBill.objects.filter(client=client).order_by('-created_at').first()
            
            if last_bill and hasattr(last_bill, 'meter_reading'):
                previous_reading = float(last_bill.meter_reading.reading_value)
            else:
                previous_reading = 0.0
                
            return JsonResponse({
                'previous_reading': previous_reading
            })
            
        except (Client.DoesNotExist, ValueError) as e:
            return JsonResponse({'error': 'Invalid client ID'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='account:login')
@admin_or_meter_reader_required
def get_bill_details(request):
    """
    API endpoint to get bill details for payment autofill.
    Returns the bill amount and other details when a bill is selected.
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        bill_id = request.GET.get('bill_id')
        try:
            bill = WaterBill.objects.select_related('name__name').get(id=bill_id)
            
            # Calculate the total payable amount
            bill_amount = float(bill.payable) if bill.payable else 0.0
            
            # Get client name
            try:
                client_name = bill.name.name.get_full_name() if bill.name and bill.name.name else 'Unknown Client'
            except AttributeError:
                client_name = 'Unknown Client'
                
            return JsonResponse({
                'success': True,
                'bill_amount': bill_amount,
                'client_name': client_name,
                'consumption': float(bill.meter_consumption) if bill.meter_consumption else 0.0,
                'penalty': float(bill.penalty) if bill.penalty else 0.0,
                'due_date': bill.due_date.strftime('%Y-%m-%d') if bill.due_date else None,
                'status': bill.status
            })
            
        except WaterBill.DoesNotExist:
            return JsonResponse({'error': 'Bill not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@admin_or_meter_reader_required
def manage_billing(request, pk):
    try:
        # Get the client and ensure they exist
        client = get_object_or_404(Client, id=pk)
        
        # Get all bills for this client, ordered by most recent
        all_bills = WaterBill.objects.filter(name=client).select_related('meter_reading').order_by('-created_at')
        
        # Get the most recent bill (current bill)
        current_bill = all_bills.first()
        
        # Check if there's already a reading for the current month
        current_month = timezone.now().month
        current_year = timezone.now().year
        has_reading_this_month = False
        
        if current_bill:
            bill_month = current_bill.created_at.month
            bill_year = current_bill.created_at.year
            has_reading_this_month = (bill_month == current_month and bill_year == current_year)
        
        # If there's already a reading for this month, redirect to dashboard with message
        if has_reading_this_month and request.method == 'GET':
            sweetify.info(
                request,
                f'This client already has a reading for {timezone.now().strftime("%B %Y")}.',
                persistent='OK'
            )
            return redirect('main:meter_reader_dashboard')
        
        # Get the previous bill (if any)
        previous_bill = all_bills.exclude(id=current_bill.id if current_bill else None).first()
        
        # Get the previous reading value (0 if no previous reading)
        previous_reading = 0
        if previous_bill and hasattr(previous_bill, 'meter_reading') and previous_bill.meter_reading:
            previous_reading = previous_bill.meter_reading.reading_value
        
        # Get reading history (last 10 readings)
        reading_history = all_bills.exclude(id=current_bill.id if current_bill else None)[:10]
        
        if request.method == 'POST':
            form = MeterReadingForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    reading_value = float(form.cleaned_data['reading'])
                    notes = form.cleaned_data.get('notes', '')
                    
                    # Calculate consumption
                    consumption = reading_value - float(previous_reading) if previous_reading else reading_value
                    
                    # Ensure consumption is not negative
                    if consumption < 0:
                        form.add_error('reading', 'Current reading cannot be less than previous reading')
                        raise forms.ValidationError('Current reading cannot be less than previous reading')
                    
                    # Create new meter reading
                    meter_reading = MeterReading.objects.create(
                        reading_value=reading_value,
                        reading_date=timezone.now(),
                        notes=notes,
                        recorded_by=request.user
                    )
                    
                    # Create new bill
                    bill = WaterBill.objects.create(
                        name=client,
                        meter_reading=meter_reading,
                        reading=reading_value,
                        meter_consumption=consumption,
                        status='Pending',
                        created_by=request.user,
                        duedate=timezone.now() + datetime.timedelta(days=30)  # Set due date to 30 days from now
                    )
                    
                    # Handle file upload if present
                    if 'meter_photo' in request.FILES:
                        bill.meter_photo = request.FILES['meter_photo']
                        bill.save()
                    
                    action = 'recorded'
                    
                    sweetify.success(
                        request,
                        f'Meter reading {action} successfully!',
                        persistent='OK'
                    )
                    
                    # Redirect based on button clicked
                    if 'next_client' in request.POST:
                        # Get next client in the list
                        next_client = Client.objects.filter(
                            id__gt=client.id,
                            assigned_meter_reader=request.user
                        ).order_by('id').first()
                        
                        if next_client:
                            return redirect('main:manage_billing', pk=next_client.id)
                        else:
                            sweetify.info(
                                request,
                                'No more clients to process.',
                                persistent='OK'
                            )
                    
                    return redirect('main:meter_reader_dashboard')
                    
                except Exception as e:
                    logger.error(f"Error saving meter reading: {str(e)}", exc_info=True)
                    sweetify.error(
                        request,
                        f'Failed to save meter reading: {str(e)}',
                        persistent='OK'
                    )
            else:
                sweetify.error(
                    request, 
                    'Please correct the errors below.',
                    persistent='OK'
                )
        else:
            # Pre-fill the form with the current reading or 0 if new
            initial_reading = 0
            if current_bill and hasattr(current_bill, 'meter_reading') and current_bill.meter_reading:
                initial_reading = current_bill.meter_reading.reading_value
                
            form = MeterReadingForm(initial={
                'reading': initial_reading,
                'previous_reading': previous_reading
            })

        context = {
            'title': f'Meter Reading - {client.name.get_full_name() or client.name.email}',
            'client': client,
            'form': form,
            'bill': current_bill,
            'previous_bill': previous_bill,
            'previous_reading': previous_reading,
            'reading_history': reading_history,
            'now': timezone.now(),
            'has_meter_reading': current_bill and hasattr(current_bill, 'meter_reading') and current_bill.meter_reading is not None
        }
        return render(request, 'main/manage_billing.html', context)
        
    except Exception as e:
        logger.error(f"Error in manage_billing: {str(e)}", exc_info=True)
        sweetify.error(
            request,
            f'An error occurred: {str(e)}',
            persistent='OK'
        )
        return redirect('main:meter_reader_dashboard')
        return redirect('main:meter_reader_dashboard')

from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_http_methods
from django.db import transaction
import sweetify

@login_required(login_url='account:login')
@require_http_methods(["POST"])
@admin_or_meter_reader_required  # Changed to allow both admin and meter readers
def record_meter_reading(request):
    """
    Handle AJAX submission of meter readings from the modal form.
    Any meter reader can add a reading for any client if no reading exists for the current month.
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    try:
        client_id = request.POST.get('client_id')
        current_reading = request.POST.get('reading_value')
        
        # Basic validation
        if not client_id or not current_reading:
            return JsonResponse({'success': False, 'message': 'Client ID and reading value are required'}, status=400)
        
        try:
            client = Client.objects.get(id=client_id)
            current_reading = Decimal(current_reading)
            
            if current_reading < 0:
                return JsonResponse({'success': False, 'message': 'Reading cannot be negative'}, status=400)
            
            # Get the current date and time
            now = timezone.now()
            
            # Check if there's already a reading for this month
            existing_reading = MeterReading.objects.filter(
                water_bill__name=client,
                reading_date__year=now.year,
                reading_date__month=now.month
            ).first()
            
            if existing_reading:
                return JsonResponse({
                    'success': False, 
                    'message': f'A reading has already been recorded for this client for {now.strftime("%B %Y")}.'
                }, status=400)
            
            # Get the last reading for this client to calculate consumption
            last_reading = MeterReading.objects.filter(
                water_bill__name=client
            ).order_by('-reading_date').first()
            
            # For new clients, previous reading is 0
            previous_reading = last_reading.reading_value if last_reading else Decimal('0.00')
            
            # Calculate consumption (current - previous)
            consumption = current_reading - previous_reading
            
            if consumption < 0:
                return JsonResponse({
                    'success': False, 
                    'message': f'Current reading ({current_reading}) cannot be less than the previous reading ({previous_reading}).'
                }, status=400)
            
            # Get the current metric rates
            try:
                metric = Metric.objects.latest('id')
            except Metric.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Billing rates have not been set up. Please contact the administrator.'
                }, status=400)
            
            # Calculate bill amount based on consumption and current rate
            bill_amount = consumption * metric.consumption_rate
            
            # Create or update the water bill and meter reading in a transaction
            with transaction.atomic():
                # Check if a bill already exists for this month
                bill, created = WaterBill.objects.get_or_create(
                    name=client,
                    created_at__year=now.year,
                    created_at__month=now.month,
                    defaults={
                        'bill': bill_amount,
                        'reading': current_reading,
                        'meter_consumption': consumption,
                        'status': 'Pending',  # Use valid status from model choices
                        'duedate': (now + timezone.timedelta(days=30)).date(),  # 30 days from now
                        'penaltydate': (now + timezone.timedelta(days=45)).date(),  # 45 days from now
                        'created_by': request.user
                    }
                )
                
                if not created:
                    # Update existing bill amount and reading if needed
                    bill.bill = bill_amount
                    bill.reading = current_reading
                    bill.meter_consumption = consumption
                    bill.save()
                
                # Create the meter reading with the water_bill field set to the created/updated bill
                meter_reading = MeterReading.objects.create(
                    water_bill=bill,  # Use the bill object we created/updated
                    reading_value=current_reading,
                    reading_date=now,
                    recorded_by=request.user,
                    notes=f'Reading recorded via dashboard. Previous: {previous_reading}, Current: {current_reading}, Consumption: {consumption}'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Meter reading and bill created successfully!',
                    'bill_id': bill.id,
                    'client_id': str(client.id),  # Include client_id for frontend updates
                    'reading_value': str(current_reading),  # Include the reading value
                    'reading_date': now.isoformat()  # Include the reading date
                })
                
        except Client.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Client not found'}, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error saving meter reading: {str(e)}'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=500)


def reports(request):
    # Handle PDF export
    if request.GET.get('export') == 'pdf':
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Get the latest metric rates
        metric = Metric.objects.first()
        consump_rate = metric.consumption_rate if metric else Decimal('1.0')
        penalty_rate = metric.penalty_rate if metric else Decimal('0.0')

        # Get bills by status
        paid_bills = WaterBill.objects.filter(status='Paid').order_by('created_at')
        pending_bills = WaterBill.objects.filter(status='Pending')
        overdue_bills = WaterBill.objects.filter(status='Overdue')
        
        # Get disconnected clients
        from main.models import Client
        disconnected_clients = Client.objects.filter(status='DISCONNECTED').count()

        # Calculate total revenue from paid bills
        total_revenue = paid_bills.aggregate(
            total=Sum(F('meter_consumption') * consump_rate)
        )['total'] or Decimal('0.0')

        # Calculate outstanding payments from pending bills
        outstanding_payments = pending_bills.aggregate(
            total=Sum(F('meter_consumption') * consump_rate)
        )['total'] or Decimal('0.0')

        # Add penalties for overdue bills
        total_overdue_penalties = overdue_bills.aggregate(
            total_penalty=Sum('penalty')
        )['total_penalty'] or Decimal('0.0')
        
        outstanding_payments += total_overdue_penalties

        # Total consumption
        total_consumption = WaterBill.objects.aggregate(
            total=Sum('meter_consumption')
        )['total'] or Decimal('0.0')

        # Billing status counts
        paid_bills_count = paid_bills.count()
        pending_bills_count = pending_bills.count()
        overdue_bills_count = overdue_bills.count()
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
        )
        elements.append(Paragraph('Water Billing System - Reports', title_style))
        elements.append(Spacer(1, 12))
        
        # Add summary statistics
        summary_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f'KSh {total_revenue:.2f}'],
            ['Outstanding Payments', f'KSh {outstanding_payments:.2f}'],
            ['Total Consumption', f'{total_consumption:.2f} units'],
            ['Paid Bills', str(paid_bills_count)],
            ['Pending Bills', str(pending_bills_count)],
            ['Overdue Bills', str(overdue_bills_count)],
            ['Disconnected Clients', str(disconnected_clients)],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 24))
        
        # Add billing details table
        billing_data = [['Status', 'Count', 'Amount']]
        billing_data.append(['Paid', str(paid_bills_count), f'KSh {total_revenue:.2f}'])
        billing_data.append(['Pending', str(pending_bills_count), f'KSh {(pending_bills.aggregate(total=Sum(F("meter_consumption") * consump_rate))["total"] or Decimal("0.0")):.2f}'])
        billing_data.append(['Overdue', str(overdue_bills_count), f'KSh {total_overdue_penalties:.2f}'])
        billing_data.append(['Disconnected Clients', str(disconnected_clients), 'N/A'])
        
        billing_table = Table(billing_data)
        billing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph('Billing Status Summary', styles['Heading2']))
        elements.append(billing_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reports.pdf"'
        
        return response
    
    # Get the latest metric rates
    metric = Metric.objects.first()
    consump_rate = metric.consumption_rate if metric else Decimal('1.0')
    penalty_rate = metric.penalty_rate if metric else Decimal('0.0')

    # Get bills by status
    paid_bills = WaterBill.objects.filter(status='Paid').order_by('created_at')
    pending_bills = WaterBill.objects.filter(status='Pending')
    overdue_bills = WaterBill.objects.filter(status='Overdue')
    
    # Get disconnected clients
    from main.models import Client
    disconnected_clients = Client.objects.filter(status='DISCONNECTED').count()

    # Calculate total revenue from paid bills
    total_revenue = paid_bills.aggregate(
        total=Sum(F('meter_consumption') * consump_rate)
    )['total'] or Decimal('0.0')

    # Calculate outstanding payments from pending bills
    outstanding_payments = pending_bills.aggregate(
        total=Sum(F('meter_consumption') * consump_rate)
    )['total'] or Decimal('0.0')

    # Add penalties for overdue bills
    total_overdue_penalties = overdue_bills.aggregate(
        total_penalty=Sum('penalty')
    )['total_penalty'] or Decimal('0.0')
    
    outstanding_payments += total_overdue_penalties

    # Total consumption
    total_consumption = WaterBill.objects.aggregate(
        total_consumption=Sum('meter_consumption')
    )['total_consumption'] or Decimal('0.0')
    
    # Monthly revenue data with more detailed information
    monthly_revenue_data = WaterBill.objects.filter(
        status='Paid'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_revenue=Sum(F('meter_consumption') * consump_rate),
        bill_count=Count('id')
    ).order_by('month')
    
    # Format for chart
    monthly_revenue = []
    for item in monthly_revenue_data:
        monthly_revenue.append({
            'month': item['month'].strftime('%b %Y'),
            'total': float(item['total_revenue'] or 0),
            'count': item['bill_count']
        })

    # Monthly consumption data with status breakdown
    monthly_consumption_data = WaterBill.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month', 'status').annotate(
        total_consumption=Sum('meter_consumption'),
        bill_count=Count('id')
    ).order_by('month', 'status')
    
    # Format for chart
    monthly_consumption = {}
    for item in monthly_consumption_data:
        month_str = item['month'].strftime('%b %Y')
        status = item['status']
        if month_str not in monthly_consumption:
            monthly_consumption[month_str] = {
                'month': month_str,
                'paid': 0,
                'pending': 0,
                'overdue': 0,
                'total': 0
            }
        monthly_consumption[month_str][status.lower()] = float(item['total_consumption'] or 0)
        monthly_consumption[month_str]['total'] += float(item['total_consumption'] or 0)
    
    # Convert to list for template
    monthly_consumption_list = list(monthly_consumption.values())

    # Billing status counts
    paid_bills_count = paid_bills.count()
    pending_bills_count = pending_bills.count()
    overdue_bills_count = overdue_bills.count()

    context = {
        'title': 'Reports',
        'total_revenue': total_revenue,
        'outstanding_payments': outstanding_payments,
        'total_consumption': total_consumption,
        'monthly_revenue_data': monthly_revenue,
        'monthly_consumption_data': monthly_consumption_list,
        'paid_bills_count': paid_bills_count,
        'pending_bills_count': pending_bills_count,
        'overdue_bills_count': overdue_bills_count,
        'disconnected_clients': disconnected_clients,
    }
    return render(request, 'main/reports.html', context)


@login_required
@admin_required
def payment_records(request):
    payments = MpesaPayment.objects.all().order_by('-created_on')
    context = {
        'title': 'M-Pesa Payment Records',
        'payments': payments
    }
    return render(request, 'main/payment_records.html', context)


class MpesaPaymentForm(forms.Form):
    amount = forms.DecimalField(
        label='Amount to Pay',
        min_value=1,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to pay'
        })
    )
    phone_number = forms.CharField(
        label='M-Pesa Phone Number',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 254712345678'
        })
    )

@login_required
def initiate_mpesa_payment(request, bill_id):
    try:
        bill = get_object_or_404(WaterBill, id=bill_id, name__name=request.user)
    except WaterBill.DoesNotExist:
        sweetify.error(request, 'Bill not found or you do not have permission to pay this bill.')
        return redirect('main:client_bill_history')

    if bill.status == 'Paid':
        sweetify.info(request, 'This bill has already been paid.')
        return redirect('main:client_bill_history')

    payable_amount = bill.payable()
    
    if request.method == 'POST':
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            phone_number = form.cleaned_data['phone_number']
            
            # Validate amount is not more than the bill amount
            if amount > payable_amount:
                sweetify.error(request, f'Payment amount cannot be more than the bill amount of KSh {payable_amount:,.2f}')
            else:
                # Format phone number (add 254 if it starts with 0 or +)
                if phone_number.startswith('0'):
                    phone_number = '254' + phone_number[1:]
                elif phone_number.startswith('+'):
                    phone_number = phone_number[1:]
                
                # Initiate M-Pesa STK push
                response_data = initiate_stk_push(
                    phone_number, 
                    int(amount), 
                    'Water Bill Payment', 
                    f'Bill {bill.id}'
                )

                if response_data and response_data.get('ResponseCode') == '0':
                    bill.checkout_request_id = response_data.get('CheckoutRequestID')
                    bill.save()
                    sweetify.success(
                        request, 
                        'Payment request sent! Please check your phone and enter your M-Pesa PIN to complete the payment.'
                    )
                    return redirect('main:client_bill_history')
                else:
                    error_message = response_data.get('errorMessage', 'Failed to initiate payment. Please try again.')
                    sweetify.error(request, error_message)
    else:
        # Pre-fill form with bill amount and user's phone number
        initial_data = {
            'amount': min(payable_amount, 1000),  # Default to bill amount or 1000, whichever is less
            'phone_number': request.user.phone_number or ''
        }
        form = MpesaPaymentForm(initial=initial_data)
    
    context = {
        'bill': bill,
        'form': form,
        'payable_amount': payable_amount,
        'title': 'Pay with M-Pesa'
    }
    return render(request, 'main/mpesa_payment.html', context)
    return redirect('client_bill_history')


import logging
logger = logging.getLogger(__name__)

@login_required(login_url='account:login')
@admin_or_meter_reader_required
def record_payment(request):
    # Get recent payments from the database
    recent_payments = list(Payment.objects.select_related(
        'bill__name__name'  # Accessing client through bill -> client -> account
    ).order_by('-payment_date')[:10])
    
    # Convert QuerySet to list of dicts for consistent handling
    recent_payments_data = []
    for p in recent_payments:
        try:
            # Safely access client name through the relationship chain
            if p.bill and p.bill.name and p.bill.name.name:
                client_name = p.bill.name.name.get_full_name()
            else:
                client_name = 'Unknown Client'
            
            recent_payments_data.append({
                'payment_date': p.payment_date,  # Keep as datetime object for template filters
                'client_name': client_name,
                'amount': float(p.amount),
                'payment_method': p.get_payment_method_display(),
                'reference_number': p.reference_number or '-',
            })
        except AttributeError as e:
            # Handle any relationship issues gracefully
            recent_payments_data.append({
                'payment_date': p.payment_date,  # Keep as datetime object for template filters
                'client_name': 'Unknown Client',
                'amount': float(p.amount),
                'payment_method': p.get_payment_method_display(),
                'reference_number': p.reference_number or '-',
            })
    
    if request.method == 'POST':
        form = PaymentRecordForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Get the form data
                    bill = form.cleaned_data['bill']
                    payment_method = form.cleaned_data['payment_method']
                    amount = form.cleaned_data['amount']
                    reference_number = form.cleaned_data['reference_number']
                    payment_date = form.cleaned_data.get('payment_date') or timezone.now()
                    notes = form.cleaned_data.get('notes', '')
                    
                    logger.info(f"Processing payment for bill ID: {bill.id}, Amount: {amount}")
                    
                    # Check if bill is already paid
                    if bill.status == 'Paid':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'This bill has already been paid.'
                        }, status=400)
                    
                    # Create the payment record
                    payment = Payment.objects.create(
                        bill=bill,
                        payment_method=payment_method,
                        amount=amount,
                        reference_number=reference_number,
                        recorded_by=request.user,
                        notes=notes,
                        payment_date=payment_date
                    )
                    
                    # Update the bill status to Paid
                    bill.status = 'Paid'
                    bill.save(update_fields=['status'])
                    
                    logger.info(f"Payment recorded successfully. Payment ID: {payment.id}")
                    
                    # Prepare the new payment data for the response
                    try:
                        client_name = bill.name.name.get_full_name() if bill.name and bill.name.name else 'Unknown Client'
                    except AttributeError:
                        client_name = 'Unknown Client'
                    
                    new_payment = {
                        'payment_date': payment.payment_date.isoformat(),  # ISO format for JSON
                        'client_name': client_name,
                        'amount': float(amount),
                        'payment_method': payment.get_payment_method_display(),
                        'reference_number': reference_number or '-',
                    }
                    
                    # Add the new payment to the beginning of the recent payments list
                    recent_payments_data.insert(0, new_payment)
                    
                    # If it's an AJAX request, return JSON response
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Payment recorded successfully!',
                            'payment': {
                                'id': payment.id,
                                'date': payment.payment_date.isoformat(),
                                'client_name': client_name,  # Use the safely accessed client_name from above
                                'amount': float(amount),
                                'method': payment.get_payment_method_display(),
                                'reference': reference_number or '-',
                                'bill_id': bill.id
                            }
                        })
                    
                    # For regular form submission - convert datetime objects to ISO strings for session storage
                    session_payments_data = []
                    for p in recent_payments_data:
                        session_payment = p.copy()
                        # Check if payment_date is already a string or needs conversion
                        if hasattr(p['payment_date'], 'isoformat'):
                            session_payment['payment_date'] = p['payment_date'].isoformat()
                        else:
                            session_payment['payment_date'] = p['payment_date']  # Already a string
                        session_payments_data.append(session_payment)
                    request.session['recent_payments'] = session_payments_data
                    sweetify.success(
                        request, 
                        'Payment recorded successfully!',
                        text=f'Amount: KSh {amount:,.2f} | Method: {payment_method} | Ref: {reference_number}',
                        timer=5000
                    )
                    return redirect('main:record_payment')
                    
            except Exception as e:
                logger.error(f"Error recording payment: {str(e)}", exc_info=True)
                sweetify.error(
                    request,
                    'Error recording payment',
                    text=f'An error occurred: {str(e)}',
                    timer=5000
                )
        else:
            # Form is invalid, show errors
            logger.warning(f"Form validation failed: {form.errors}")
            sweetify.error(
                request,
                'Please correct the errors below',
                persistent=True
            )
    else:
        # Initialize form with only pending bills
        form = PaymentRecordForm()
    
    context = {
        'title': 'Record Payment',
        'form': form,
        'recent_payments': recent_payments_data,  # Use processed data with client names
        'active_page': 'record_payment'
    }
    return render(request, 'main/record_payment.html', context)


def mpesa_callback(request):
    try:
        payload = json.loads(request.body)
        stk_callback = payload.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')

        if not checkout_request_id:
            return HttpResponse(status=400) # Bad request if no checkout ID

        # Log the entire callback
        MpesaPayment.objects.create(
            checkout_request_id=checkout_request_id,
            result_code=result_code,
            result_desc=result_desc,
        )

        if str(result_code) == '0':
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            amount = next((item['Value'] for item in callback_metadata if item['Name'] == 'Amount'), None)
            transaction_id = next((item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'), None)
            phone_number = next((item['Value'] for item in callback_metadata if item['Name'] == 'PhoneNumber'), None)

            try:
                bill = WaterBill.objects.get(checkout_request_id=checkout_request_id)
                bill.status = 'Paid'
                bill.save()

                # Update the payment log with bill details
                payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
                payment.bill = bill
                payment.transaction_id = transaction_id
                payment.amount = amount
                payment.phone_number = phone_number
                payment.save()

            except WaterBill.DoesNotExist:
                # Handle case where bill is not found but payment was made
                pass

    except json.JSONDecodeError:
        return HttpResponse(status=400) # Invalid JSON
    except Exception as e:
        # Log unexpected errors
        return HttpResponse(status=500)

    return HttpResponse(status=200)


@login_required(login_url='login')
@admin_required
def register_customer(request):
    if request.method == 'POST':
        form = MeterReaderClientCreationForm(request.POST)
        if form.is_valid():
            # Create the user account
            user = Account.objects.create_user(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password']
            )
            user.role = Account.Role.CUSTOMER # Set role to Customer
            user.verified = True  # Admin/Meter Reader created users are automatically verified
            user.save()

            # Create the associated client profile
            Client.objects.create(
                name=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                contact_number=form.cleaned_data['contact_number'],
                address=form.cleaned_data['address'],
                status='Pending'
            )
            
            sweetify.success(request, 'New client has been registered successfully!')
            # Redirect based on user role
            if request.user.role == 'METER_READER':
                return redirect('meter_reader_dashboard')
            else:
                return redirect('users') # For admins
        else:
            sweetify.error(request, 'Please correct the errors below.')
    else:
        form = MeterReaderClientCreationForm()
    
    context = {
        'title': 'Register New Client',
        'form': form
    }
    return render(request, 'account/admin_register_user.html', context)









@login_required
def generate_bill_pdf(request, bill_id):
    try:
        bill = WaterBill.objects.get(id=bill_id)
        # Ensure the user has permission to view this bill
        is_owner = (request.user.role == Account.Role.CUSTOMER and bill.name.name == request.user)
        is_admin = (request.user.role == Account.Role.ADMIN)
        
        if not (is_owner or is_admin):
            return HttpResponse("Unauthorized", status=403)

    except WaterBill.DoesNotExist:
        return HttpResponse("Bill not found", status=404)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Add content to the PDF
    textob.textLine("Denkam Water Billing System")
    textob.textLine("-" * 50)
    textob.textLine(f"Bill ID: {bill.id}")
    textob.textLine(f"Client: {bill.name.name.get_full_name()}")
    textob.textLine(f"Date: {bill.created_at.strftime('%Y-%m-%d')}")
    textob.textLine(f"Status: {bill.status}")
    textob.textLine("-" * 50)
    
    # Calculate previous reading safely
    previous_reading = 0
    if bill.meter_consumption is not None and bill.reading is not None:
        previous_reading = bill.reading - bill.meter_consumption

    textob.textLine(f"Previous Reading: {previous_reading}")
    textob.textLine(f"Current Reading: {bill.reading or 0}")
    textob.textLine(f"Consumption (m³): {bill.meter_consumption or 0}")
    textob.textLine(" ")
    textob.textLine(f"Amount Payable: KES {bill.payable()}")

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename=f'bill_{bill.id}.pdf')


@login_required
@admin_required
def generate_client_list_pdf(request):
    clients = Client.objects.select_related('name').all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Denkam Water Billing System - Client List", styles['h1'])
    elements.append(title)
    
    # Table Data
    data = [['ID', 'Full Name', 'Email', 'Contact', 'Address', 'Status']]
    for client in clients:
        data.append([
            client.id,
            client.name.get_full_name(),
            client.name.email,
            client.contact_number,
            client.address,
            client.status
        ])
        
    # Create Table
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    elements.append(table)
    
    doc.build(elements)
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='client_list.pdf')

