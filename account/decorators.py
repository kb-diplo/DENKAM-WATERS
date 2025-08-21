from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from .models import Account

def admin_required(function=None, redirect_field_name=None, login_url='account:login'):
    '''
    Decorator for views that checks that the user is an admin.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def meter_reader_required(function=None, redirect_field_name=None, login_url='account:login'):
    '''
    Decorator for views that checks that the user is a meter reader.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == Account.Role.METER_READER,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def customer_required(function=None, redirect_field_name=None, login_url='account:login'):
    '''
    Decorator for views that checks that the user is a customer.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == Account.Role.CUSTOMER,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def customer_or_admin_required(function=None, redirect_field_name=None, login_url='account:login'):
    '''
    Decorator for views that checks that the user is a customer or an admin.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.role == Account.Role.CUSTOMER or u.role == Account.Role.ADMIN),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_or_meter_reader_required(function=None, redirect_field_name=None, login_url='account:login'):
    '''
    Decorator for views that checks that the user is an admin or a meter reader.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.role == Account.Role.ADMIN or u.role == Account.Role.METER_READER),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
