from rest_framework import serializers
from customers.models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    outstanding_balance = serializers.SerializerMethodField()
    last_reading = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'user', 'full_name', 'phone_number', 'address', 
            'city', 'postal_code', 'outstanding_balance', 'last_reading',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_outstanding_balance(self, obj):
        from billing.models import Bill
        from django.db.models import Sum
        balance = Bill.objects.filter(
            customer=obj,
            status__in=['pending', 'overdue']
        ).aggregate(total=Sum('amount'))['total']
        return balance or 0

    def get_last_reading(self, obj):
        from meter_readings.models import MeterReading
        reading = MeterReading.objects.filter(
            customer=obj
        ).order_by('-reading_date').first()
        if reading:
            return {
                'value': reading.reading_value,
                'date': reading.reading_date,
                'meter_id': reading.meter.meter_id
            }
        return None 