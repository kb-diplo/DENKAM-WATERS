from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from billing.models import Bill, Tariff, Invoice

class CustomAdminSite(AdminSite):
    site_header = 'Denkam Waters Administration'
    site_title = 'Denkam Waters Admin Portal'
    index_title = 'Welcome to Denkam Waters Administration'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def index(self, request, extra_context=None):
        # Get statistics
        total_users = get_user_model().objects.count()
        total_bills = Bill.objects.count()
        total_customers = Customer.objects.count()
        
        # Get recent activity
        recent_activity = []
        for model in [Bill, Customer, Invoice]:
            recent_activity.extend(
                model.objects.all().order_by('-created_at')[:5]
            )
        recent_activity = sorted(recent_activity, key=lambda x: x.created_at, reverse=True)[:10]
        
        # Calculate bill amounts using rate_per_unit and consumption
        monthly_stats = Bill.objects.annotate(
            month=TruncMonth('created_at'),
            consumption=F('current_reading') - F('previous_reading'),
            bill_amount=F('consumption') * F('rate_per_unit')
        ).values('month').annotate(
            count=Count('id'),
            total=Sum('bill_amount')
        ).order_by('month')
        
        context = {
            'total_users': total_users,
            'total_bills': total_bills,
            'total_customers': total_customers,
            'recent_activity': recent_activity,
            'monthly_stats': monthly_stats,
            **(extra_context or {}),
        }
        return super().index(request, context)

admin_site = CustomAdminSite(name='admin')

# Register models with the custom admin site
admin_site.register(get_user_model(), UserAdmin)
admin_site.register(Customer)
admin_site.register(Bill)
admin_site.register(Tariff)
admin_site.register(Invoice) 