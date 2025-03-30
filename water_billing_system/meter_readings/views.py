from django.shortcuts import render, redirect
from .models import MeterReading
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

class MeterReadingListView(ListView):
    model = MeterReading
    template_name = 'meter_readings/list.html'
    context_object_name = 'readings'

class MeterReadingCreateView(CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/create.html'
    success_url = '/meter-readings/'