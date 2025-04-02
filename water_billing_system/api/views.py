from rest_framework import viewsets, permissions
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from accounts.models import User
from customers.models import Customer, Meter
from meter_readings.models import MeterReading
from billing.models import Bill, Tariff
from payments.models import Payment, Receipt
from .serializers import (
    UserSerializer, CustomerSerializer, MeterSerializer,
    MeterReadingSerializer, BillSerializer, TariffSerializer,
    PaymentSerializer, ReceiptSerializer
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

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_auth_token(request):
    """
    Refresh the user's authentication token
    """
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        token = Token.objects.create(user=request.user)
        return Response({
            'token': token.key,
            'created': token.created,
            'user_id': token.user_id
        })
    except Token.DoesNotExist:
        return Response({
            'error': 'No token found for user'
        }, status=404)