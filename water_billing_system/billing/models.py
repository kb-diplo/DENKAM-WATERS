from django.db import models
from customers.models import Customer
from meter_readings.models import MeterReading
from django.utils import timezone

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} @ KES {self.rate_per_unit}/unit"

class Bill(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bills')
    billing_period = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    previous_reading = models.DecimalField(max_digits=10, decimal_places=2)
    current_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    usage = models.DecimalField(max_digits=10, decimal_places=2)
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(default=timezone.now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-billing_period']
    
    def __str__(self):
        return f"Bill #{self.id} for {self.customer.name} - {self.billing_period}"
    
    def save(self, *args, **kwargs):
        # Calculate usage and amount due if not set
        if not self.usage:
            self.usage = self.current_reading - self.previous_reading
        if not self.amount_due:
            self.amount_due = (self.usage * self.tariff.rate_per_unit) + self.tariff.fixed_charge
        super().save(*args, **kwargs)

class Invoice(models.Model):
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} for Bill #{self.bill.id}"