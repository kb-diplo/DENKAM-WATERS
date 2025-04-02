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
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from .models import Bill, Tariff, Invoice
from .forms import BillForm, TariffForm, InvoiceForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from io import BytesIO

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

@login_required
def bill_list(request):
    if request.user.role in ['supplier', 'admin']:
        bills = Bill.objects.all().order_by('-created_at')
    else:
        # For customers, only show their own bills
        bills = Bill.objects.filter(customer=request.user.customer_profile).order_by('-created_at')
    
    paginator = Paginator(bills, 10)
    page = request.GET.get('page')
    bills = paginator.get_page(page)
    return render(request, 'Billing/bill_list.html', {'bills': bills})

@login_required
def bill_create(request):
    if request.user.role not in ['supplier', 'admin']:
        messages.error(request, 'You do not have permission to create bills.')
        return redirect('billing:bill_list')
        
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save()
            messages.success(request, 'Bill created successfully.')
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        form = BillForm()
    return render(request, 'billing/bill_form.html', {'form': form})

@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    # Check if user has permission to view this bill
    if request.user.role not in ['supplier', 'admin'] and bill.customer != request.user.customer_profile:
        messages.error(request, 'You do not have permission to view this bill.')
        return redirect('billing:bill_list')
    return render(request, 'billing/bill_detail.html', {'bill': bill})

@login_required
def bill_update(request, pk):
    if request.user.role not in ['supplier', 'admin']:
        messages.error(request, 'You do not have permission to update bills.')
        return redirect('billing:bill_list')
        
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            bill = form.save()
            messages.success(request, 'Bill updated successfully.')
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        form = BillForm(instance=bill)
    return render(request, 'billing/bill_form.html', {'form': form})

@login_required
def bill_delete(request, pk):
    if request.user.role not in ['supplier', 'admin']:
        messages.error(request, 'You do not have permission to delete bills.')
        return redirect('billing:bill_list')
        
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        bill.delete()
        messages.success(request, 'Bill deleted successfully.')
        return redirect('billing:bill_list')
    return render(request, 'billing/bill_delete.html', {'bill': bill})

@login_required
def generate_invoice(request, pk):
    if request.user.role not in ['supplier', 'admin']:
        messages.error(request, 'You do not have permission to generate invoices.')
        return redirect('billing:bill_list')
        
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
def bill_pdf(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    template = get_template('billing/bill_pdf.html')
    html = template.render({'bill': bill})
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO buffer as its "file"
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    
    # If the PDF creation failed, return error response
    if pisa_status.err:
        return HttpResponse('We had some errors with creating the PDF <pre>' + html + '</pre>')
    
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.bill_number}.pdf"'
    
    return response

@login_required
def bill_mark_paid(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        bill.status = 'paid'
        bill.save()
        messages.success(request, 'Bill marked as paid successfully.')
        return redirect('billing:bill_detail', pk=bill.pk)
    return render(request, 'billing/bill_detail.html', {'bill': bill})

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    paginator = Paginator(invoices, 10)
    page = request.GET.get('page')
    invoices = paginator.get_page(page)
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, 'Invoice created successfully.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'billing/invoice_form.html', {'form': form})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    template = get_template('billing/invoice_pdf.html')
    html = template.render({'invoice': invoice})
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO buffer as its "file"
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    
    # If the PDF creation failed, return error response
    if pisa_status.err:
        return HttpResponse('We had some errors with creating the PDF <pre>' + html + '</pre>')
    
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    return response