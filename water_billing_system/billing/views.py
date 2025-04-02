from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, 
    CreateView, 
    DetailView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Bill, Tariff, Invoice
from .forms import BillForm, TariffForm
from django.contrib.auth.decorators import login_required

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin']

class BillListView(StaffRequiredMixin, ListView):
    model = Bill
    template_name = 'Billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 10

class BillCreateView(StaffRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'Billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)

class BillDetailView(StaffRequiredMixin, DetailView):
    model = Bill
    template_name = 'Billing/bill_detail.html'

class BillUpdateView(StaffRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = 'Billing/bill_form.html'
    
    def get_success_url(self):
        return reverse_lazy('billing:bill_detail', kwargs={'pk': self.object.pk})

class BillDeleteView(StaffRequiredMixin, DeleteView):
    model = Bill
    template_name = 'Billing/bill_confirm_delete.html'
    success_url = reverse_lazy('billing:bill_list')

def generate_invoice(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    
    # Create or get existing invoice
    invoice, created = Invoice.objects.get_or_create(bill=bill)
    if created:
        invoice.invoice_number = f"INV-{bill.id}-{bill.billing_period}"
        invoice.save()
    
    template_path = 'Billing/invoice_pdf.html'
    context = {'invoice': invoice}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

class TariffListView(StaffRequiredMixin, ListView):
    model = Tariff
    template_name = 'Billing/tariff_list.html'
    context_object_name = 'tariffs'

class TariffCreateView(StaffRequiredMixin, CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'Billing/tariff_form.html'
    success_url = reverse_lazy('billing:tariff_list')

class TariffUpdateView(StaffRequiredMixin, UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'Billing/tariff_form.html'
    success_url = reverse_lazy('billing:tariff_list')

class TariffDeleteView(StaffRequiredMixin, DeleteView):
    model = Tariff
    template_name = 'Billing/tariff_confirm_delete.html'
    success_url = reverse_lazy('billing:tariff_list')

@login_required
def bill_list(request):
    if request.user.role in ['admin', 'supplier']:
        bills = Bill.objects.all().order_by('-billing_period')
    else:
        bills = Bill.objects.filter(customer__user=request.user).order_by('-billing_period')
    return render(request, 'Billing/bill_list.html', {'bills': bills})

@login_required
def bill_create(request):
    if request.user.role not in ['admin', 'supplier']:
        messages.error(request, "You don't have permission to create bills.")
        return redirect('billing:bill_list')
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save()
            messages.success(request, 'Bill created successfully.')
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        form = BillForm()
    return render(request, 'Billing/bill_form.html', {'form': form, 'title': 'Create Bill'})

@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.user.role not in ['admin', 'supplier'] and bill.customer.user != request.user:
        messages.error(request, "You don't have permission to view this bill.")
        return redirect('billing:bill_list')
    return render(request, 'Billing/bill_detail.html', {'bill': bill})

@login_required
def bill_update(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.user.role not in ['admin', 'supplier']:
        messages.error(request, "You don't have permission to update bills.")
        return redirect('billing:bill_list')
    
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bill updated successfully.')
            return redirect('billing:bill_detail', pk=pk)
    else:
        form = BillForm(instance=bill)
    return render(request, 'Billing/bill_form.html', {'form': form, 'title': 'Update Bill'})

@login_required
def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.user.role not in ['admin', 'supplier']:
        messages.error(request, "You don't have permission to delete bills.")
        return redirect('billing:bill_list')
    
    if request.method == 'POST':
        bill.delete()
        messages.success(request, 'Bill deleted successfully.')
        return redirect('billing:bill_list')
    return render(request, 'Billing/bill_confirm_delete.html', {'bill': bill})