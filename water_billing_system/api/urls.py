from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CustomerViewSet, MeterViewSet,
    MeterReadingViewSet, BillViewSet, TariffViewSet,
    PaymentViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'meters', MeterViewSet)
router.register(r'meter-readings', MeterReadingViewSet)
router.register(r'bills', BillViewSet)
router.register(r'tariffs', TariffViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]