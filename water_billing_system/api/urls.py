from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from accounts.api.views import RegisterAPIView, LoginAPIView, LogoutAPIView

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'meters', views.MeterViewSet)
router.register(r'readings', views.MeterReadingViewSet)
router.register(r'bills', views.BillViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'receipts', views.ReceiptViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('token/', views.obtain_auth_token, name='token'),
    path('token/refresh/', views.refresh_auth_token, name='token_refresh'),
    path('accounts/register/', RegisterAPIView.as_view(), name='api-register'),
    path('accounts/login/', LoginAPIView.as_view(), name='api-login'),
    path('accounts/logout/', LogoutAPIView.as_view(), name='api-logout'),
]