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
from .models import Payment, Receipt
from .forms import PaymentForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin']

class PaymentListView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

class PaymentCreateView(StaffRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:payment_list')
    
    def get_initial(self):
        initial = super().get_initial()
        bill_id = self.request.GET.get('bill')
        if bill_id:
            from billing.models import Bill
            try:
                bill = Bill.objects.get(pk=bill_id)
                initial['bill'] = bill
                initial['customer'] = bill.customer
                initial['amount_paid'] = bill.amount_due
            except Bill.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.received_by = self.request.user
        return super().form_valid(form)

class PaymentDetailView(StaffRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'

class PaymentUpdateView(StaffRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('payments:payment_detail', kwargs={'pk': self.object.pk})

class PaymentDeleteView(StaffRequiredMixin, DeleteView):
    model = Payment
    template_name = 'payments/payment_confirm_delete.html'
    success_url = reverse_lazy('payments:payment_list')

def generate_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    # Create or get existing receipt
    receipt, created = Receipt.objects.get_or_create(payment=payment)
    if created:
        receipt.receipt_number = f"RCP-{payment.id}-{payment.payment_date.strftime('%Y%m%d')}"
        receipt.save()
    
    template_path = 'payments/receipt_pdf.html'
    context = {'receipt': receipt}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.receipt_number}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response