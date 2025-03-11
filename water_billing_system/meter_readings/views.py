from django.shortcuts import render, redirect
from .forms import MeterReadingForm

def input_meter_reading(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to a success page
    else:
        form = MeterReadingForm()
    return render(request, 'meter_readings/input.html', {'form': form})