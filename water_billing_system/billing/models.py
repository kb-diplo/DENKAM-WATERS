from django.db import models
from customers.models import Customer
from meter_readings.models import MeterReading

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.name} @ KES {self.rate_per_unit}/unit"

class Bill(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_period = models.CharField(max_length=20)
    usage = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.name}"