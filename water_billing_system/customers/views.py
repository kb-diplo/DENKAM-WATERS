from django.urls import reverse_lazy
from django.views.generic import (
    ListView, 
    CreateView, 
    DetailView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Customer
from .forms import CustomerForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin', 'meter_reader']

class CustomerListView(StaffRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerCreateView(StaffRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CustomerDetailView(StaffRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'

class CustomerUpdateView(StaffRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})

class CustomerDeleteView(StaffRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')