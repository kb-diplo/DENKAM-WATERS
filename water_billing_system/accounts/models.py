# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)