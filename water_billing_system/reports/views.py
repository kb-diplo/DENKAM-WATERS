from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages
from xhtml2pdf import pisa
from datetime import datetime, timedelta
import json
from billing.models import Bill
from payments.models import Payment
from customers.models import Customer
from .models import Report
from .forms import DateRangeForm, ReportTypeForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin']

class ReportListView(StaffRequiredMixin, ListView):
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10

class SalesReportView(StaffRequiredMixin, TemplateView):
    template_name = 'reports/sales_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateRangeForm(self.request.GET or None)
        
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            # Default to last 30 days if no dates provided
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            form = DateRangeForm(initial={
                'start_date': start_date,
                'end_date': end_date
            })
        
        # Get bills in date range
        bills = Bill.objects.filter(
            created_at__date__range=(start_date, end_date)
        ).order_by('billing_period')
        
        # Calculate totals
        total_bills = bills.count()
        total_amount = sum(bill.amount_due for bill in bills)
        paid_amount = sum(bill.amount_due for bill in bills if bill.status == 'paid')
        unpaid_amount = total_amount - paid_amount
        
        context.update({
            'form': form,
            'start_date': start_date,
            'end_date': end_date,
            'bills': bills,
            'total_bills': total_bills,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'unpaid_amount': unpaid_amount,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Generate report and save to database
            bills = Bill.objects.filter(
                created_at__date__range=(start_date, end_date)
            ).order_by('billing_period')
            
            total_amount = sum(bill.amount_due for bill in bills)
            paid_amount = sum(bill.amount_due for bill in bills if bill.status == 'paid')
            
            report_data = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_bills': bills.count(),
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'unpaid_amount': total_amount - paid_amount,
            }
            
            report = Report.objects.create(
                report_type='sales',
                generated_by=request.user,
                start_date=start_date,
                end_date=end_date,
                data=report_data
            )
            
            messages.success(request, 'Sales report generated successfully!')
            return HttpResponseRedirect(reverse('reports:report_list'))
        
        return self.render_to_response(self.get_context_data(form=form))

class PaymentsReportView(StaffRequiredMixin, TemplateView):
    template_name = 'reports/payments_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateRangeForm(self.request.GET or None)
        
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            # Default to last 30 days if no dates provided
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            form = DateRangeForm(initial={
                'start_date': start_date,
                'end_date': end_date
            })
        
        # Get payments in date range
        payments = Payment.objects.filter(
            payment_date__date__range=(start_date, end_date)
        ).order_by('-payment_date')
        
        # Calculate totals
        total_payments = payments.count()
        total_amount = sum(payment.amount_paid for payment in payments)
        
        # Group by payment method
        payment_methods = {}
        for method in Payment.PAYMENT_METHOD_CHOICES:
            method_payments = payments.filter(payment_method=method[0])
            method_total = sum(p.amount_paid for p in method_payments)
            payment_methods[method[1]] = {
                'count': method_payments.count(),
                'total': method_total
            }
        
        context.update({
            'form': form,
            'start_date': start_date,
            'end_date': end_date,
            'payments': payments,
            'total_payments': total_payments,
            'total_amount': total_amount,
            'payment_methods': payment_methods,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Generate report and save to database
            payments = Payment.objects.filter(
                payment_date__date__range=(start_date, end_date)
            ).order_by('-payment_date')
            
            total_amount = sum(payment.amount_paid for payment in payments)
            
            payment_methods = {}
            for method in Payment.PAYMENT_METHOD_CHOICES:
                method_payments = payments.filter(payment_method=method[0])
                method_total = sum(p.amount_paid for p in method_payments)
                payment_methods[method[0]] = {
                    'name': method[1],
                    'count': method_payments.count(),
                    'total': method_total
                }
            
            report_data = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_payments': payments.count(),
                'total_amount': total_amount,
                'payment_methods': payment_methods,
            }
            
            report = Report.objects.create(
                report_type='payments',
                generated_by=request.user,
                start_date=start_date,
                end_date=end_date,
                data=report_data
            )
            
            messages.success(request, 'Payments report generated successfully!')
            return HttpResponseRedirect(reverse('reports:report_list'))
        
        return self.render_to_response(self.get_context_data(form=form))

class BalancesReportView(StaffRequiredMixin, TemplateView):
    template_name = 'reports/balances_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        customers = Customer.objects.all()
        customer_balances = []
        
        for customer in customers:
            unpaid_bills = customer.bills.filter(status__in=['pending', 'overdue'])
            total_balance = sum(bill.amount_due for bill in unpaid_bills)
            
            if total_balance > 0:
                customer_balances.append({
                    'customer': customer,
                    'balance': total_balance,
                    'unpaid_bills': unpaid_bills.count()
                })
        
        # Sort by highest balance first
        customer_balances.sort(key=lambda x: x['balance'], reverse=True)
        
        context['customer_balances'] = customer_balances
        context['total_balance'] = sum(item['balance'] for item in customer_balances)
        return context
    
    def post(self, request, *args, **kwargs):
        # Generate report and save to database
        customers = Customer.objects.all()
        customer_balances = []
        
        for customer in customers:
            unpaid_bills = customer.bills.filter(status__in=['pending', 'overdue'])
            total_balance = sum(bill.amount_due for bill in unpaid_bills)
            
            if total_balance > 0:
                customer_balances.append({
                    'customer_id': customer.id,
                    'customer_name': customer.name,
                    'meter_id': customer.meter_id,
                    'balance': total_balance,
                    'unpaid_bills': unpaid_bills.count()
                })
        
        report_data = {
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'customer_balances': customer_balances,
            'total_balance': sum(item['balance'] for item in customer_balances),
        }
        
        report = Report.objects.create(
            report_type='balances',
            generated_by=request.user,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            data=report_data
        )
        
        messages.success(request, 'Customer balances report generated successfully!')
        return HttpResponseRedirect(reverse('reports:report_list'))

def generate_report_pdf(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    template_path = 'reports/report_pdf.html'
    context = {'report': report}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Denkam_Report_{report.report_type}_{report.id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response