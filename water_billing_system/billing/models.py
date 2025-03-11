
# Create your models here.
from django.db import models
from customers.models import Customer

class Bill(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_period = models.CharField(max_length=50)
    usage = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.amount_due}"