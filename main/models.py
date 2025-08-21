from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import Account
from django.utils import timezone
import datetime
import string
import secrets


class Client(models.Model):
    """
    Client model that extends the Account model with additional client-specific information.
    The name field is a OneToOne link to the Account model which contains authentication info.
    """
    STATUS_CHOICES = (
        ('Connected', 'Connected'),
        ('Disconnected', 'Disconnected'),
        ('Pending', 'Pending')
    )
    
    name = models.OneToOneField(
        Account, 
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='User Account',
        help_text='Link to the user account for authentication'
    )
    meter_number = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        help_text='Unique meter number for the client',
        verbose_name='Meter Number'
    )
    middle_name = models.CharField(
        max_length=30, 
        null=True, 
        blank=True,
        verbose_name='Middle Name'
    )
    contact_number = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        verbose_name='Phone Number',
        help_text='Format: +254...'
    )
    address = models.TextField(
        max_length=500,
        help_text='Full physical address of the client'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text='Connection status of the client'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_meter_reader = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_clients',
        limit_choices_to={'role': 'METER_READER'},
        help_text='Meter reader responsible for this client'
    )

    class Meta:
        ordering = ['name__last_name', 'name__first_name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.name.get_full_name() or 'Unnamed Client'}"
        
    def get_full_name(self):
        """Get the full name of the client from the associated account."""
        return self.name.get_full_name()
        
    def get_email(self):
        """Get the email of the client from the associated account."""
        return self.name.email
        
    def get_contact_number(self):
        """Get the formatted contact number."""
        return self.contact_number or 'Not provided'


class WaterBill(models.Model):
    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    )
    
    created_by = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_bills',
        help_text='Staff member who created this bill',
        verbose_name='Created By'
    )
    name = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE,
        related_name='water_bills',
        help_text='Client this bill belongs to',
        verbose_name='Client'
    )
    reading = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        help_text='Current meter reading',
        verbose_name='Meter Reading'
    )
    meter_consumption = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        help_text='Units consumed (current reading - previous reading)',
        verbose_name='Consumption (units)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default='Pending',
        help_text='Payment status of the bill',
        verbose_name='Status'
    )
    duedate = models.DateField(
        null=True,
        help_text='Due date for payment',
        verbose_name='Due Date'
    )
    penaltydate = models.DateField(
        null=True,
        blank=True,
        help_text='Date when penalty will be applied if bill is not paid',
        verbose_name='Penalty Date'
    )
    bill = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        help_text='Bill amount before penalties',
        verbose_name='Base Bill Amount'
    )
    penalty = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text='Penalty amount for late payment',
        verbose_name='Penalty Amount'
    )
    checkout_request_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text='Payment gateway reference ID',
        verbose_name='Payment Reference'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this bill was created',
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this bill was last updated',
        verbose_name='Updated At'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Water Bill'
        verbose_name_plural = 'Water Bills'

    
    @property
    def metrics(self):
        if not hasattr(self, '_metrics'):
            self._metrics = Metric.objects.first()
        return self._metrics

    def compute_bill(self):
        if self.metrics and self.metrics.consumption_rate and self.meter_consumption is not None:
            return self.meter_consumption * self.metrics.consumption_rate
        return 0

    def calculate_penalty(self):
        if self.metrics and self.metrics.penalty_rate and self.penaltydate and self.penaltydate <= datetime.date.today():
            return self.metrics.penalty_rate
        return 0

    
    def payable(self):
        bill = self.compute_bill()
        pen = self.calculate_penalty()
        return bill + pen


    def __str__(self):
        return f'{self.name}'


class MeterReading(models.Model):
    """
    Model to store meter readings for water consumption.
    Each reading is linked to a water bill.
    """
    water_bill = models.OneToOneField(
        WaterBill,
        on_delete=models.CASCADE,
        related_name='meter_reading',
        null=True,
        blank=True,
        help_text='The water bill this reading is associated with'
    )
    reading_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='The meter reading value in cubic meters (m³)',
        validators=[MinValueValidator(0, 'Reading cannot be negative')]
    )
    reading_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time when the reading was taken'
    )
    recorded_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_readings',
        help_text='User who recorded this reading'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Any additional notes about this reading'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reading_date']
        verbose_name = 'Meter Reading'
        verbose_name_plural = 'Meter Readings'

    def __str__(self):
        return f"{self.reading_value} m³ - {self.reading_date.strftime('%Y-%m-%d %H:%M')}"


class Metric(models.Model):
    """
    Model to store water consumption and penalty rates.
    There should only be one instance of this model in the database.
    """
    consumption_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text='Rate per unit of water consumed (in KES)',
        verbose_name='Consumption Rate',
        validators=[
            MinValueValidator(0, message='Rate cannot be negative'),
            MaxValueValidator(10000, message='Rate is too high')
        ]
    )
    penalty_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text='Penalty amount applied to overdue bills',
        verbose_name='Penalty Amount',
        validators=[
            MinValueValidator(0, message='Penalty cannot be negative'),
            MaxValueValidator(10000, message='Penalty is too high')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Billing Metric'
        verbose_name_plural = 'Billing Metrics'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.consumption_rate} per unit, {self.penalty_rate} penalty"


class Payment(models.Model):
    """
    Model to track all types of payments (Mpesa, Bank Transfer, Cash)
    """
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    bill = models.ForeignKey(
        'WaterBill',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text='Optional: Link to the bill being paid',
        verbose_name='Bill'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='Amount must be greater than 0')],
        help_text='Amount paid',
        verbose_name='Amount (KES)'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        help_text='Payment method used',
        verbose_name='Payment Method'
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Reference number for the payment (e.g., M-Pesa code, bank reference)',
        verbose_name='Reference Number'
    )
    recorded_by = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
        help_text='Staff who recorded this payment',
        verbose_name='Recorded By'
    )
    payment_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time when payment was made',
        verbose_name='Payment Date'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Any additional notes about this payment',
        verbose_name='Notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Bill #{self.id} - {self.name} - {self.get_status_display()} - KES {self.amount} - {self.payment_date.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Call the parent save first to ensure we have a PK for the payment
        super().save(*args, **kwargs)
        
        # If this payment is linked to a bill, update the bill status if fully paid
        if self.bill:
            # Calculate total paid including this payment
            total_paid = sum(p.amount for p in self.bill.payments.all())
            bill_payable = self.bill.payable()
            
            # Update bill status based on payment (only Paid or Pending)
            if total_paid >= bill_payable:
                self.bill.status = 'Paid'
            else:
                self.bill.status = 'Pending'
                
            # Save the bill to update its status
            self.bill.save(update_fields=['status'])
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

