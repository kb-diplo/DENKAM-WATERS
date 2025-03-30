
# Create your models here.
from django.db import models
from customers.models import Customer

class MeterReading(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    reading_date = models.DateField()
    reading_value = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reading_date']