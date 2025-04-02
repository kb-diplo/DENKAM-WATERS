from django import forms
from .models import Bill, Tariff, Invoice
from customers.models import Customer
from meter_readings.models import MeterReading

class BillForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="Select a customer",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    billing_period = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'month',
            'class': 'form-control'
        })
    )
    
    previous_reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    
    current_reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    
    rate_per_unit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    
    status = forms.ChoiceField(
        choices=Bill.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any additional notes here...'
        })
    )

    class Meta:
        model = Bill
        fields = ['customer', 'billing_period', 'previous_reading', 'current_reading', 
                 'rate_per_unit', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        previous_reading = cleaned_data.get('previous_reading')
        current_reading = cleaned_data.get('current_reading')
        
        if previous_reading and current_reading:
            if current_reading < previous_reading:
                raise forms.ValidationError(
                    "Current reading cannot be less than previous reading."
                )
        
        return cleaned_data

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'rate_per_unit', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['bill', 'invoice_number', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }