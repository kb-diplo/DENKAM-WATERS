from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from customers.models import Customer
from .serializers import CustomerSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_customer(request):
    """
    Register a new customer.
    """
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        return Response({
            'id': customer.id,
            'name': customer.name,
            'email': customer.user.email,
            'message': 'Customer registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customers.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Override to allow unauthenticated access for customer registration.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on user role.
        """
        user = self.request.user
        if user.role == 'customer':
            return Customer.objects.filter(user=user)
        return Customer.objects.all()

    @action(detail=True, methods=['get'])
    def bills(self, request, pk=None):
        """
        Get all bills for a specific customer.
        """
        customer = self.get_object()
        bills = customer.bill_set.all().order_by('-billing_period')
        from billing.api.serializers import BillSerializer
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """
        Get all payments for a specific customer.
        """
        customer = self.get_object()
        payments = customer.payment_set.all().order_by('-payment_date')
        from payments.api.serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def meter_readings(self, request, pk=None):
        """
        Get all meter readings for a specific customer.
        """
        customer = self.get_object()
        readings = customer.meter_readings.all().order_by('-reading_date')
        from meter_readings.api.serializers import MeterReadingSerializer
        serializer = MeterReadingSerializer(readings, many=True)
        return Response(serializer.data) 