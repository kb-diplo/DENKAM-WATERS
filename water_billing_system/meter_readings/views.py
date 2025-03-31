from django.urls import reverse_lazy
from django.views.generic import (
    ListView, 
    CreateView, 
    DetailView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import MeterReading
from .forms import MeterReadingForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['supplier', 'admin', 'meter_reader']

class MeterReadingListView(StaffRequiredMixin, ListView):
    model = MeterReading
    template_name = 'meter_readings/reading_list.html'
    context_object_name = 'readings'
    paginate_by = 10

class MeterReadingCreateView(StaffRequiredMixin, CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/reading_form.html'
    success_url = reverse_lazy('meter_readings:reading_list')
    
    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

class MeterReadingDetailView(StaffRequiredMixin, DetailView):
    model = MeterReading
    template_name = 'meter_readings/reading_detail.html'

class MeterReadingUpdateView(StaffRequiredMixin, UpdateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter_readings/reading_form.html'
    
    def get_success_url(self):
        return reverse_lazy('meter_readings:reading_detail', kwargs={'pk': self.object.pk})

class MeterReadingDeleteView(StaffRequiredMixin, DeleteView):
    model = MeterReading
    template_name = 'meter_readings/reading_confirm_delete.html'
    success_url = reverse_lazy('meter_readings:reading_list')