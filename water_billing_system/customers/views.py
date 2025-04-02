from django.urls import reverse_lazy
from django.views.generic import (
    ListView, 
    CreateView, 
    DetailView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Customer, Meter
from .forms import CustomerForm, MeterForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin', 'meter_reader']

class CustomerListView(StaffRequiredMixin, ListView):
    model = Customer
    template_name = 'Customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerCreateView(StaffRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'Customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CustomerDetailView(StaffRequiredMixin, DetailView):
    model = Customer
    template_name = 'Customers/customer_detail.html'

class CustomerUpdateView(StaffRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'Customers/customer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})

class CustomerDeleteView(StaffRequiredMixin, DeleteView):
    model = Customer
    template_name = 'Customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')

# Meter Views
class MeterListView(StaffRequiredMixin, ListView):
    model = Meter
    template_name = 'Customers/meter_list.html'
    context_object_name = 'meters'
    paginate_by = 10

class MeterCreateView(StaffRequiredMixin, CreateView):
    model = Meter
    form_class = MeterForm
    template_name = 'Customers/meter_form.html'
    success_url = reverse_lazy('customers:meter_list')
    
    def form_valid(self, form):
        form.instance.installed_by = self.request.user
        return super().form_valid(form)

class MeterUpdateView(StaffRequiredMixin, UpdateView):
    model = Meter
    form_class = MeterForm
    template_name = 'Customers/meter_form.html'
    
    def get_success_url(self):
        return reverse_lazy('customers:meter_list')

class MeterDeleteView(StaffRequiredMixin, DeleteView):
    model = Meter
    template_name = 'Customers/meter_confirm_delete.html'
    success_url = reverse_lazy('customers:meter_list')