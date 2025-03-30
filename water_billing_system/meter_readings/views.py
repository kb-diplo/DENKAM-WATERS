from django.shortcuts import render, redirect
from .models import MeterReading
from .forms import MeterReadingForm
from django.views.generic import CreateView, ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import User

def is_supplier(user):
    return user.is_authenticated and user.is_supplier

@login_required
@user_passes_test(is_supplier)
def add_meter_reading(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.staff = request.user
            reading.save()
            return redirect('meter_reading_success')
    else:
        form = MeterReadingForm()
    
    return render(request, 'meter_readings/input.html', {'form': form})


class MeterReadingCreateView(CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/create.html'
    success_url = '/meter-readings/'

class MeterReadingListView(ListView):
    model = MeterReading
    template_name = 'meter_readings/list.html'
    context_object_name = 'readings'
    paginate_by = 20