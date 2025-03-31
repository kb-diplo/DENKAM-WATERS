from django import forms
from .models import Bill, Tariff
from customers.models import Customer
from meter_readings.models import MeterReading

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['customer', 'billing_period', 'start_date', 'end_date', 
                 'previous_reading', 'current_reading', 'tariff', 'due_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tariff'].queryset = Tariff.objects.filter(is_active=True)

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'rate_per_unit', 'fixed_charge', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }