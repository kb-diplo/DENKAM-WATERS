from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.urls import reverse
from .forms import MeterReaderRegistrationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import admin_required, meter_reader_required
from .forms import CustomerRegistrationForm, MeterReaderRegistrationForm, RegistrationForm, AdminRegistrationForm, AdminUserCreationForm
from main.models import *
from django.conf import settings
import sweetify
import random as r
import smtplib


def landingpage(request):
    return render(request, 'account/landingpage.html')





def login_view(request):
    role = request.GET.get('role')
    
    # If this is a POST request, process the form data
    if request.method == 'POST':
        # Get the email and password from the POST data
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Basic validation
        if not email or not password:
            return render(request, 'account/login.html', {
                'error': 'Please provide both email and password',
                'role': role,
                'email': email
            })
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            sweetify.success(request, 'Login Successful')
            
            # Redirect based on user role
            if user.role == Account.Role.ADMIN:
                if not Metric.objects.exists():
                    Metric.objects.create(consumption_rate=1, penalty_rate=1)
                return HttpResponseRedirect(reverse('main:dashboard'))
            elif user.role == Account.Role.METER_READER:
                return HttpResponseRedirect(reverse('main:meter_reader_dashboard'))
            elif user.role == Account.Role.CUSTOMER:
                return HttpResponseRedirect(reverse('main:client_dashboard'))
            else:
                return HttpResponseRedirect(reverse('main:landingpage'))
        else:
            # Return an 'invalid login' error message
            return render(request, 'account/login.html', {
                'error': 'Invalid email or password. Please try again.',
                'role': role,
                'email': email
            })
    
    # If this is a GET request, just show the login form

    # Clear any existing messages
    storage = messages.get_messages(request)
    storage.used = True

    return render(request, 'account/login.html', {'role': role})








def logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)
    return redirect('account:login')


def customer_register_view(request):
    form = CustomerRegistrationForm()
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Customer account created successfully.')
            return HttpResponseRedirect(reverse('login'))
        else:
            sweetify.error(request, 'Please correct the errors below.')
    context = {
        'form': form,
        'title': 'Customer Registration'
    }
    return render(request, 'account/register.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def admin_register_view(request):
    form = AdminRegistrationForm()
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Administrator account created successfully.')
            return HttpResponseRedirect(reverse('users'))
        else:
            sweetify.error(request, 'Please correct the errors below.')
    context = {
        'form': form,
        'title': 'Administrator Registration'
    }
    return render(request, 'account/register.html', context)


import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

@login_required(login_url='login')
@admin_required
def meter_reader_register_view(request):
    logger.info('Meter reader registration view started.')
    form = RegistrationForm()
    if request.method == 'POST':
        logger.info('POST request received.')
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logger.info('Form is valid.')
            user = form.save(commit=False)
            user.role = Account.Role.METER_READER
            user.save()
            sweetify.success(request, 'Meter Reader account created successfully.')
            logger.info('Meter reader created successfully.')
            return HttpResponseRedirect(reverse('users'))
        else:
            logger.error(f'Form is invalid: {form.errors}')
            sweetify.error(request, 'Please correct the errors below.')
    context = {
        'form': form,
        'title': 'Meter Reader Registration'
    }
    logger.info('Rendering registration page.')
    return render(request, 'account/meter_reader_register.html', context)


@login_required(login_url='account:login')
@admin_required
def admin_register_user_view(request):
    """
    Allows an admin to register a new client account with enhanced form handling.
    """
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Save the user and create client profile (handled in form's save method)
                user = form.save()
                
                # Log the action
                logger.info(f'Admin {request.user.email} created new client account: {user.email}')
                
                sweetify.success(
                    request,
                    'Client account created successfully!',
                    text=f'Account for {user.get_full_name()} has been created.',
                    persistent='OK'
                )
                return redirect('main:clients')
                
            except Exception as e:
                logger.error(f'Error creating client account: {str(e)}')
                sweetify.error(
                    request,
                    'Error creating account',
                    text='An error occurred while creating the client account. Please try again.',
                    persistent='OK'
                )
        else:
            # Form is invalid, show error messages
            error_messages = []
            for field, errors in form.errors.items():
                field_label = field.replace('_', ' ').title()
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
            
            sweetify.error(
                request,
                'Please correct the errors below',
                text='\n'.join(error_messages) or 'There was an error with your submission.',
                persistent='OK'
            )
    else:
        form = CustomerRegistrationForm()

    context = {
        'title': 'Register New Client',
        'form': form,
        'active_tab': 'clients',
    }
    return render(request, 'account/admin_register_user.html', context)


@login_required(login_url='account:login')
@admin_required
def admin_register_meter_reader_view(request):
    """
    Allows an admin to register a new meter reader account.
    """
    if request.method == 'POST':
        form = MeterReaderRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=True)
                sweetify.success(
                    request, 
                    'Meter Reader account created successfully!',
                    text=f'Login credentials have been sent to {user.email}.'
                )
                return redirect('main:users')
            except Exception as e:
                logging.error(f"Error creating meter reader account: {str(e)}")
                sweetify.error(
                    request,
                    'Error creating meter reader account',
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
        form = MeterReaderRegistrationForm()

    context = {
        'title': 'Register New Meter Reader',
        'form': form,
    }
    # Debug output
    print("Rendering template with form:", form)
    print("Form fields:", form.fields.keys())
    return render(request, 'account/admin_register_meter_reader.html', context)


@login_required(login_url='account:login')
@meter_reader_required
def meter_reader_register_user_view(request):
    form = CustomerRegistrationForm()
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = Account.Role.CUSTOMER
            user.save()
            sweetify.success(request, 'Client account created successfully!')
            return redirect('account:meter_reader_dashboard')
    context = {
        'form': form,
        'title': 'Register Client'
    }
    return render(request, 'account/register.html', context)


def meter_reader_dashboard(request):
    context = {
        'title': 'Meter Reader Dashboard'
    }
    return render(request, 'account/meter_reader_dashboard.html', context)
