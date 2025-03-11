from django import forms
from .models import MeterReading

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['customer', 'reading_date', 'reading_value', 'notes']