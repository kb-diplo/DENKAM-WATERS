from rest_framework import serializers
from payments.models import Payment
from django.utils import timezone

class PaymentSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateTimeField(required=False, default=timezone.now)

    class Meta:
        model = Payment
        fields = [
            'id', 'customer', 'bill', 'amount_paid',
            'payment_date', 'payment_method', 'transaction_id',
            'received_by', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Set payment_date to now if not provided
        if 'payment_date' not in validated_data:
            validated_data['payment_date'] = timezone.now()
        
        # Create the payment
        payment = Payment.objects.create(**validated_data)
        return payment 