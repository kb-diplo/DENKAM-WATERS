from django import forms
from .models import MeterReading

class MeterReadingForm(forms.ModelForm):
    reading_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    reading_value = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = MeterReading
        fields = ['customer', 'reading_date', 'reading_value', 'notes']