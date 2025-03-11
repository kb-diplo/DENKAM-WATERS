from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from customers.models import Customer
from billing.models import Bill  
from payments.models import Payment


@login_required
def customer_dashboard(request):
    customer = Customer.objects.get(user=request.user)
    bills = Bill.objects.filter(customer=customer)
    payments = Payment.objects.filter(customer=customer)
    return render(request, 'customers/dashboard.html', {
        'customer': customer,
        'bills': bills,
        'payments': payments,
    })

@login_required
def billing_history(request):
    customer = Customer.objects.get(user=request.user)
    bills = Bill.objects.filter(customer=customer)
    return render(request, 'customers/billing_history.html', {
        'bills': bills,
    })

@login_required
def payment_history(request):
    customer = Customer.objects.get(user=request.user)
    payments = Payment.objects.filter(customer=customer)
    return render(request, 'customers/payment_history.html', {
        'payments': payments,
    })

@login_required
def account_management(request):
    customer = Customer.objects.get(user=request.user)
    return render(request, 'customers/account_management.html', {
        'customer': customer,
    })

@login_required
def update_account(request):
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        # Update customer details
        customer.name = request.POST.get('name')
        customer.address = request.POST.get('address')
        customer.contact = request.POST.get('contact')
        customer.save()
        return redirect('account_management')
    return render(request, 'customers/update_account.html', {
        'customer': customer,
    })

@login_required
def water_usage(request):
    customer = Customer.objects.get(user=request.user)
    readings = MeterReading.objects.filter(customer=customer)
    return render(request, 'customers/water_usage.html', {
        'readings': readings,
    })


def home(request):
    return render(request, 'home.html')