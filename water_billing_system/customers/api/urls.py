from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, register_customer

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_customer, name='register-customer'),
] 