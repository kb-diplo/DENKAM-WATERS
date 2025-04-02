from django.contrib import admin
from .models import Tariff, Bill, Invoice

class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'customer', 'billing_period', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'billing_period']
    search_fields = ['bill_number', 'customer__full_name']
    readonly_fields = ['bill_number', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Bill Information', {
            'fields': ['bill_number', 'customer', 'billing_period', 'status']
        }),
        ('Readings and Rate', {
            'fields': ['previous_reading', 'current_reading', 'rate_per_unit']
        }),
        ('Additional Information', {
            'fields': ['notes', 'created_at', 'updated_at']
        }),
    ]
    inlines = [InvoiceInline]

admin.site.register(Tariff)
admin.site.register(Invoice)