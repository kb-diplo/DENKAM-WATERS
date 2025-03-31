from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("End date must be after start date.")
            if (end_date - start_date).days > 365:
                raise ValidationError("Date range cannot exceed one year.")
        
        return cleaned_data

class ReportTypeForm(forms.Form):
    REPORT_TYPE_CHOICES = [
        ('sales', 'Sales Report'),
        ('payments', 'Payments Report'),
        ('balances', 'Customer Balances Report'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='sales'
    )