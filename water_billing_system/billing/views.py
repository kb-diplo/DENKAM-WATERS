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

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin']

class BillListView(StaffRequiredMixin, ListView):
    model = Bill
    template_name = 'billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 10

class BillCreateView(StaffRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)

class BillDetailView(StaffRequiredMixin, DetailView):
    model = Bill
    template_name = 'billing/bill_detail.html'

class BillUpdateView(StaffRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    
    def get_success_url(self):
        return reverse_lazy('billing:bill_detail', kwargs={'pk': self.object.pk})

class BillDeleteView(StaffRequiredMixin, DeleteView):
    model = Bill
    template_name = 'billing/bill_confirm_delete.html'
    success_url = reverse_lazy('billing:bill_list')

def generate_invoice(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    
    # Create or get existing invoice
    invoice, created = Invoice.objects.get_or_create(bill=bill)
    if created:
        invoice.invoice_number = f"INV-{bill.id}-{bill.billing_period}"
        invoice.save()
    
    template_path = 'billing/invoice_pdf.html'
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
    template_name = 'billing/tariff_list.html'
    context_object_name = 'tariffs'

class TariffCreateView(StaffRequiredMixin, CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'billing/tariff_form.html'
    success_url = reverse_lazy('billing:tariff_list')

class TariffUpdateView(StaffRequiredMixin, UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'billing/tariff_form.html'
    success_url = reverse_lazy('billing:tariff_list')

class TariffDeleteView(StaffRequiredMixin, DeleteView):
    model = Tariff
    template_name = 'billing/tariff_confirm_delete.html'
    success_url = reverse_lazy('billing:tariff_list')