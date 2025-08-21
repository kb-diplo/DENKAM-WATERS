from django.contrib import admin
from .models import Client, WaterBill, Metric

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'meter_number', 'status', 'contact_number', 'assigned_meter_reader_display')
    list_select_related = ('name', 'assigned_meter_reader')
    search_fields = ('name__first_name', 'name__last_name', 'name__email', 'meter_number', 'contact_number')
    list_filter = ('status', 'created_at', 'assigned_meter_reader')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'meter_number', 'middle_name', 'contact_number')
        }),
        ('Address Information', {
            'fields': ('address',)
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_meter_reader')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.name.get_full_name() if obj.name else 'N/A'
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'name__first_name'
    
    def email(self, obj):
        return obj.name.email if obj.name else 'N/A'
    email.short_description = 'Email'
    
    def assigned_meter_reader_display(self, obj):
        return obj.assigned_meter_reader.get_full_name() if obj.assigned_meter_reader else 'Unassigned'
    assigned_meter_reader_display.short_description = 'Meter Reader'

@admin.register(WaterBill)
class WaterBillAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'reading', 'get_meter_consumption', 'status', 'duedate', 'get_payable')
    list_select_related = ('name', 'name__name')
    search_fields = ('name__name__first_name', 'name__name__last_name', 'name__meter_number')
    list_filter = ('status', 'duedate', 'created_at')
    readonly_fields = ('get_payable', 'created_at', 'updated_at', 'get_meter_consumption')
    date_hierarchy = 'duedate'
    
    fieldsets = (
        ('Billing Information', {
            'fields': ('name', 'reading', 'get_meter_consumption', 'status')
        }),
        ('Payment Details', {
            'fields': ('bill', 'penalty', 'get_payable')
        }),
        ('Dates', {
            'fields': ('duedate', 'penaltydate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name(self, obj):
        return f"{obj.name.name.get_full_name()}" if obj.name and obj.name.name else 'N/A'
    client_name.short_description = 'Client'
    client_name.admin_order_field = 'name__name__first_name'
    
    def get_meter_consumption(self, obj):
        if obj.reading is not None and hasattr(obj, 'previous_reading') and obj.previous_reading is not None:
            return obj.reading - obj.previous_reading
        return 0
    get_meter_consumption.short_description = 'Consumption (m³)'
    get_meter_consumption.admin_order_field = 'reading'
    
    def get_payable(self, obj):
        return f"KES {obj.payable():.2f}" if hasattr(obj, 'payable') and callable(getattr(obj, 'payable')) else 'N/A'
    get_payable.short_description = 'Amount Payable'

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('consumption_rate', 'penalty_rate', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Billing Rates', {
            'fields': ('consumption_rate', 'penalty_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Allow adding only if no metrics exist yet
        return Metric.objects.count() == 0
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only metric
        return False





