from django.utils import timezone
from .models import Bill, Tariff
from customers.models import Customer
from meter_readings.models import MeterReading

def calculate_bill(customer_id):
    customer = Customer.objects.get(pk=customer_id)
    readings = MeterReading.objects.filter(customer=customer).order_by('reading_date')
    
    if len(readings) < 2:
        return None  # Not enough readings to calculate usage
        
    last_reading = readings[len(readings)-1]
    previous_reading = readings[len(readings)-2]
    
    usage = last_reading.reading_value - previous_reading.reading_value
    current_tariff = Tariff.objects.latest('effective_date')
    amount_due = usage * current_tariff.rate_per_unit
    
    bill = Bill.objects.create(
        customer=customer,
        billing_period=f"{previous_reading.reading_date} to {last_reading.reading_date}",
        usage=usage,
        amount_due=amount_due,
        status='Pending'
    )
    
    return bill