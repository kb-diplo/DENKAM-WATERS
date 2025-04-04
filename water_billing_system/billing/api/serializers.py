from rest_framework import serializers
from billing.models import Bill
from payments.models import Payment
from customers.models import Customer

class BillSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            'id', 'customer', 'customer_name', 'billing_period',
            'previous_reading', 'current_reading', 'rate_per_unit',
            'amount', 'status', 'status_display', 'due_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'amount', 'status']

    def get_customer_name(self, obj):
        return f"{obj.customer.user.first_name} {obj.customer.user.last_name}".strip() or obj.customer.user.username

    def get_status_display(self, obj):
        return obj.get_status_display()

    def create(self, validated_data):
        # Get the customer's last reading
        customer = validated_data['customer']
        last_reading = customer.meter_readings.order_by('-reading_date').first()
        
        if not last_reading:
            raise serializers.ValidationError("No previous meter reading found for this customer")
        
        # Set the previous reading to the last reading
        validated_data['previous_reading'] = last_reading.reading_value
        
        # Create the bill
        bill = Bill.objects.create(**validated_data)
        return bill

class PaymentSerializer(serializers.ModelSerializer):
    bill_number = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'bill', 'bill_number', 'customer_name',
            'amount', 'payment_date', 'payment_method',
            'payment_method_display', 'status', 'status_display',
            'reference_number', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'reference_number', 'status']

    def get_bill_number(self, obj):
        return obj.bill.bill_number

    def get_customer_name(self, obj):
        return f"{obj.bill.customer.user.first_name} {obj.bill.customer.user.last_name}".strip() or obj.bill.customer.user.username

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()

    def create(self, validated_data):
        bill = validated_data['bill']
        amount = validated_data['amount']

        # Check if payment amount is valid
        if amount > bill.amount:
            raise serializers.ValidationError("Payment amount cannot exceed bill amount")

        # Create the payment
        payment = Payment.objects.create(**validated_data)

        # Update bill status if payment is completed
        if payment.status == 'completed':
            bill.status = 'paid'
            bill.save()

        return payment 