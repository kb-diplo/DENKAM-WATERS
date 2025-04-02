from django.db import models
from django.core.validators import MinValueValidator
from customers.models import Customer
from meter_readings.models import MeterReading
from django.utils import timezone
import uuid

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
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    
    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bills')
    billing_period = models.DateField()
    previous_reading = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_reading = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-billing_period', '-created_at']
        
    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        super().save(*args, **kwargs)
    
    def generate_bill_number(self):
        year = timezone.now().year
        month = timezone.now().month
        unique_id = str(uuid.uuid4().hex)[:6]
        return f'BILL-{year}{month:02d}-{unique_id}'
    
    @property
    def units_consumed(self):
        return max(0, self.current_reading - self.previous_reading)
    
    @property
    def total_amount(self):
        return self.units_consumed * self.rate_per_unit
    
    @property
    def vat_amount(self):
        return self.total_amount * 0.16  # 16% VAT
    
    @property
    def total_with_vat(self):
        return self.total_amount + self.vat_amount
    
    def __str__(self):
        return f"Bill {self.bill_number} - {self.customer.full_name} ({self.billing_period})"

class Invoice(models.Model):
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} for Bill #{self.bill.id}"