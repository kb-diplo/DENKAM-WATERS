from django import forms
from .models import MeterReading
from customers.models import Meter

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['meter', 'reading_date', 'reading_value', 'notes']
        widgets = {
            'reading_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meter'].queryset = Meter.objects.filter(is_active=True)