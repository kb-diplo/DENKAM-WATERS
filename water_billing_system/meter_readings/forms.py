from django import forms
from .models import MeterReading
from customers.models import Customer

class MeterReadingForm(forms.ModelForm):
    reading_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = MeterReading
        fields = ['customer', 'reading_date', 'reading_value', 'notes']
        widgets = {
            'reading_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


    def clean_reading_value(self):
        value = self.cleaned_data['reading_value']
        if value < 0:
            raise forms.ValidationError("Reading value cannot be negative")
        return value

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        reading_value = cleaned_data.get('reading_value')
        
        if customer and reading_value:
            last_reading = MeterReading.objects.filter(
                customer=customer
            ).order_by('-reading_date').first()
            
            if last_reading and reading_value < last_reading.reading_value:
                raise forms.ValidationError(
                    f"New reading ({reading_value}) must be higher than last reading ({last_reading.reading_value})"
                )
        return cleaned_data