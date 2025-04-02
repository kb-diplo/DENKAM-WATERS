from rest_framework import serializers
from accounts.models import User
from customers.models import Customer, Meter
from meter_readings.models import MeterReading
from billing.models import Bill, Tariff
from payments.models import Payment, Receipt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = '__all__'

class MeterReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterReading
        fields = '__all__'

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Receipt
        fields = '__all__'