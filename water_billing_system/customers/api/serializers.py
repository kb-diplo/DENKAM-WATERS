from rest_framework import serializers
from django.contrib.auth import get_user_model
from customers.models import Customer
from django.db import IntegrityError

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)
    meter_id = serializers.CharField(required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'address', 'contact', 'meter_id',
            'email', 'password', 'first_name', 'last_name', 'username',
            'phone', 'address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_meter_id(self, value):
        """
        Validate that the meter ID is unique.
        """
        if value and Customer.objects.filter(meter_id=value).exists():
            raise serializers.ValidationError("A customer with this meter ID already exists.")
        return value

    def create(self, validated_data):
        # Create user first
        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'username': validated_data.pop('username'),
            'role': 'customer',
            'phone': validated_data.pop('phone', None),
            'address': validated_data.pop('address', None)
        }
        user = User.objects.create_user(**user_data)
        
        # Generate a unique meter ID if not provided
        meter_id = validated_data.pop('meter_id', None)
        if not meter_id:
            # Try to create with generated ID, retry if there's a conflict
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    meter_id = f"M{user.id:05d}{attempt if attempt > 0 else ''}"
                    customer = Customer.objects.create(
                        user=user,
                        name=validated_data.pop('name', f"{user.first_name} {user.last_name}".strip() or user.username),
                        address=validated_data.pop('address', user.address or "Address not provided"),
                        contact=validated_data.pop('contact', user.phone or "Contact not provided"),
                        meter_id=meter_id
                    )
                    return customer
                except IntegrityError:
                    if attempt == max_attempts - 1:
                        raise serializers.ValidationError("Could not generate a unique meter ID. Please try again.")
                    continue
        
        # If meter_id was provided, create customer with it
        try:
            customer = Customer.objects.create(
                user=user,
                name=validated_data.pop('name', f"{user.first_name} {user.last_name}".strip() or user.username),
                address=validated_data.pop('address', user.address or "Address not provided"),
                contact=validated_data.pop('contact', user.phone or "Contact not provided"),
                meter_id=meter_id
            )
            return customer
        except IntegrityError:
            raise serializers.ValidationError("A customer with this meter ID already exists.") 