from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'contact', 'meter_id']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }