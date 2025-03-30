from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bill
from meter_readings.models import MeterReading

@receiver(post_save, sender=MeterReading)
def create_bill(sender, instance, created, **kwargs):
    if created:
        # Get previous reading
        prev_reading = MeterReading.objects.filter(
            customer=instance.customer,
            reading_date__lt=instance.reading_date
        ).order_by('-reading_date').first()
        
        if prev_reading:
            # Calculate usage and create bill
            usage = instance.reading_value - prev_reading.reading_value
            Bill.objects.create(
                customer=instance.customer,
                billing_period=f"{prev_reading.reading_date.date()} to {instance.reading_date.date()}",
                usage=usage,
                amount_due=usage * 50,  # Replace with tariff calculation
                status='pending'
            )