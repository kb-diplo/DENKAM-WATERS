from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from customers.models import Customer

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ₦{self.rate_per_unit}/unit"

class Bill(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_period = models.DateField()
    previous_reading = models.DecimalField(max_digits=10, decimal_places=2)
    current_reading = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def consumption(self):
        return self.current_reading - self.previous_reading

    @property
    def amount(self):
        return self.consumption * self.rate_per_unit

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate bill number: BILL-YYYYMMDD-XXXX
            date = timezone.now().strftime('%Y%m%d')
            last_bill = Bill.objects.filter(bill_number__startswith=f'BILL-{date}').order_by('-bill_number').first()
            if last_bill:
                last_number = int(last_bill.bill_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.bill_number = f'BILL-{date}-{new_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_number} - {self.customer.name}"

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE)
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number: INV-YYYYMMDD-XXXX
            date = timezone.now().strftime('%Y%m%d')
            last_invoice = Invoice.objects.filter(invoice_number__startswith=f'INV-{date}').order_by('-invoice_number').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.invoice_number = f'INV-{date}-{new_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.bill.customer.name}"