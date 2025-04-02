from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    meter_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Meter: {self.meter_id})"

class Meter(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='meters')
    installation_date = models.DateField()
    last_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Meter {self.id} for {self.customer.name}"