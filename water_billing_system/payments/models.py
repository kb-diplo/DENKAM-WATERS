from django.db import models
from customers.models import Customer
from billing.models import Bill

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    received_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment of KES {self.amount_paid} for Bill #{self.bill.id}"
    
    def save(self, *args, **kwargs):
        # Update bill status if payment covers the amount due
        if self.amount_paid >= self.bill.amount_due:
            self.bill.status = 'paid'
            self.bill.save()
        super().save(*args, **kwargs)

class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Receipt {self.receipt_number} for Payment #{self.payment.id}"