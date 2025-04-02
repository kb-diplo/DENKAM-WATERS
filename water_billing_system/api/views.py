from rest_framework import viewsets, permissions
from accounts.models import User
from customers.models import Customer, Meter
from meter_readings.models import MeterReading
from billing.models import Bill, Tariff
from payments.models import Payment
from .serializers import (
    UserSerializer, CustomerSerializer, MeterSerializer,
    MeterReadingSerializer, BillSerializer, TariffSerializer,
    PaymentSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class MeterViewSet(viewsets.ModelViewSet):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    permission_classes = [permissions.IsAuthenticated]

class MeterReadingViewSet(viewsets.ModelViewSet):
    queryset = MeterReading.objects.all()
    serializer_class = MeterReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]