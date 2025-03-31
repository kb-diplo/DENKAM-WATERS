from django import forms
from .models import Payment
from customers.models import Customer
from billing.models import Bill

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['customer', 'bill', 'amount_paid', 'payment_date', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bill'].queryset = Bill.objects.filter(status__in=['pending', 'overdue'])
        
        if 'customer' in self.data:
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['bill'].queryset = Bill.objects.filter(customer_id=customer_id, status__in=['pending', 'overdue'])
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['bill'].queryset = self.instance.customer.bills.filter(status__in=['pending', 'overdue'])