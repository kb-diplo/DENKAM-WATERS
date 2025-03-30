from django import forms
from .models import MeterReading

class MeterReadingForm(forms.ModelForm):
    reading_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = MeterReading
        fields = ['customer', 'reading_date', 'reading_value', 'notes']