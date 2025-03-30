from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='customer'
    )
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(max_length=20)
    meter_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name