from django import forms
from .models import Customer, Meter

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'contact', 'meter_id']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class MeterForm(forms.ModelForm):
    installation_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    last_reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Meter
        fields = ['customer', 'installation_date', 'last_reading', 'is_active']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
        }