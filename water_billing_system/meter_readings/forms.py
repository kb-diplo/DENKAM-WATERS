from django import forms
from .models import MeterReading

class MeterReadingForm(forms.ModelForm):
    reading_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = MeterReading
        fields = ['customer', 'reading_date', 'reading_value', 'notes']