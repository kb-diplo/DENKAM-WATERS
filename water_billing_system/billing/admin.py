from django.contrib import admin
from .models import Bill, Tariff, Invoice

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate_per_unit', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'customer', 'billing_period', 'consumption', 'amount', 'status', 'created_at')
    list_filter = ('status', 'billing_period', 'created_at')
    search_fields = ('bill_number', 'customer__name', 'notes')
    readonly_fields = ('bill_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def consumption(self, obj):
        return f"{obj.consumption} units"
    consumption.short_description = 'Consumption'

    def amount(self, obj):
        return f"₦{obj.amount:,.2f}"
    amount.short_description = 'Amount'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'bill', 'due_date', 'created_at', 'updated_at')
    list_filter = ('due_date', 'created_at', 'updated_at')
    search_fields = ('invoice_number', 'bill__bill_number', 'bill__customer__name', 'notes')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)