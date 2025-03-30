from django.db import models
from customers.models import Customer

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

class Bill(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_period = models.CharField(max_length=50)
    usage = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)