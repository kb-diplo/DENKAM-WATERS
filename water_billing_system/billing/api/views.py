from rest_framework import viewsets, permissions
from rest_framework.response import Response
from billing.models import Bill
from .serializers import BillSerializer

class BillViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing bills.
    """
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter bills based on user role.
        """
        user = self.request.user
        if user.role == 'customer':
            return Bill.objects.filter(customer__user=user)
        return Bill.objects.all() 