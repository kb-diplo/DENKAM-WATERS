"""
URL configuration for water_billing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .admin import admin_site

# Customize admin site
admin.site.site_header = 'Denkam Waters Administration'
admin.site.site_title = 'Denkam Waters Admin Portal'
admin.site.index_title = 'Welcome to Denkam Waters Management Portal'

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),  # Redirect root to admin
    path('admin/', admin_site.urls),
    path('', include('billing.urls')),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('meter-readings/', include('meter_readings.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler403 = 'water_billing_system.views.custom_permission_denied_view'
handler404 = 'water_billing_system.views.custom_page_not_found_view'
handler500 = 'water_billing_system.views.custom_error_view'