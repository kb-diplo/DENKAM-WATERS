from django.contrib import admin
from .models import Tariff, Bill, Invoice

class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0

class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'billing_period', 'amount_due', 'status', 'due_date')
    list_filter = ('status', 'billing_period')
    search_fields = ('customer__name', 'customer__meter_id')
    inlines = [InvoiceInline]

admin.site.register(Tariff)
admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice)