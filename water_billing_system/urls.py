from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # Make accounts the root URL
    path('billing/', include('billing.urls')),
    path('customers/', include('customers.urls')),
    path('meter-readings/', include('meter_readings.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 