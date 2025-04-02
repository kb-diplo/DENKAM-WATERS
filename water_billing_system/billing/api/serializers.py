from rest_framework import serializers
from billing.models import Bill

class BillSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            'id', 'customer', 'customer_name', 'billing_period',
            'amount', 'status', 'status_display', 'due_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_customer_name(self, obj):
        return f"{obj.customer.user.first_name} {obj.customer.user.last_name}".strip() or obj.customer.user.username

    def get_status_display(self, obj):
        return obj.get_status_display() 