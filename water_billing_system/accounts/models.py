from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from customers.models import Customer

class User(AbstractUser):
    ROLE_CHOICES = (
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('meter_reader', 'Meter Reader'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        if instance.role == 'customer':
            Customer.objects.create(
                user=instance,
                name=f"{instance.first_name} {instance.last_name}".strip() or instance.username,
                address=instance.address or "Address not provided",
                contact=instance.phone or "Contact not provided",
                meter_id=f"M{instance.id:05d}"  # Generate a meter ID based on user ID
            )