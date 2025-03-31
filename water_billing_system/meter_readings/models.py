from django.db import models
from customers.models import Customer, Meter

class MeterReading(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='readings')
    reading_date = models.DateTimeField()
    reading_value = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reading_date']
    
    def __str__(self):
        return f"Reading {self.reading_value} for {self.meter.customer.name} on {self.reading_date}"

    def save(self, *args, **kwargs):
        # Update the meter's last reading when saving
        self.meter.last_reading = self.reading_value
        self.meter.save()
        super().save(*args, **kwargs)