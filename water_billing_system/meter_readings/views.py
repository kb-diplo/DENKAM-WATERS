from django.shortcuts import render, redirect
from .models import MeterReading
from .forms import MeterReadingForm
from django.contrib.auth.decorators import login_required, user_passes_test


def input_meter_reading(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Redirect to a success page
    else:
        form = MeterReadingForm()
    return render(request, 'meter_readings/input.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role == 'supplier')
def meter_reading_create(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.save()
            return redirect('meter_reading_list')
    else:
        form = MeterReadingForm()
    return render(request, 'meter_readings/create.html', {'form': form})

@login_required
def meter_reading_list(request):
    if request.user.role == 'supplier':
        readings = MeterReading.objects.all()
    else:
        customer = request.user.customer
        readings = MeterReading.objects.filter(customer=customer)
    return render(request, 'meter_readings/list.html', {'readings': readings})