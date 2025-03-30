
# Create your models here.
from django.db import models
from customers.models import Customer

class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    
    class Meta:
        ordering = ['-period_end']