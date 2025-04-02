from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .models import UserProfile

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile updates here
        pass
    
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def dashboard_view(request):
    context = {}
    
    if request.user.role in ['supplier', 'admin']:
        from customers.models import Customer
        from billing.models import Bill
        
        context['customer_count'] = Customer.objects.count()
        context['paid_bills_count'] = Bill.objects.filter(status='paid').count()
        context['pending_bills_count'] = Bill.objects.filter(status='pending').count()
        context['overdue_bills_count'] = Bill.objects.filter(status='overdue').count()
    elif request.user.role == 'customer':
        from billing.models import Bill
        from payments.models import Payment
        
        customer = request.user.customer_profile
        context['recent_bills'] = Bill.objects.filter(customer=customer).order_by('-billing_period')[:5]
        context['recent_payments'] = Payment.objects.filter(customer=customer).order_by('-payment_date')[:5]
    
    return render(request, 'dashboard.html', context)