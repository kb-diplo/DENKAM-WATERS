from django.db import models
from django.utils import timezone
from django.conf import settings
from main.models import WaterBill

class MpesaPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD = 'mpesa'
    
    # Using a more specific related_name to avoid conflicts
    bill = models.ForeignKey(WaterBill, on_delete=models.CASCADE, related_name='mpesa_payment_transactions')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    is_successful = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    # Using TextField instead of JSONField for better compatibility with older Django versions
    raw_callback_data = models.TextField(null=True, blank=True, help_text='Raw JSON data from M-Pesa callback')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = 'M-Pesa Payment'
        verbose_name_plural = 'M-Pesa Payments'
    
    def __str__(self):
        return f"M-Pesa Payment {self.transaction_id or self.checkout_request_id or 'N/A'}"
    
    def save(self, *args, **kwargs):
        # Update completed_on when payment is marked as successful
        if self.is_successful and not self.completed_on:
            self.completed_on = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def payment_method(self):
        return self.PAYMENT_METHOD
    
    def mark_as_successful(self, receipt_number=None, notes=None):
        """Mark payment as successful"""
        self.status = 'completed'
        self.is_successful = True
        self.completed_on = timezone.now()
        if receipt_number:
            self.receipt_number = receipt_number
        if notes:
            self.notes = notes
        self.save()
    
    def mark_as_failed(self, error_message=None):
        """Mark payment as failed"""
        self.status = 'failed'
        self.is_successful = False
        if error_message:
            self.notes = f"Payment failed: {error_message}"
        self.save()
