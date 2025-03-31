from django.contrib import admin
from .models import Payment, Receipt

class ReceiptInline(admin.StackedInline):
    model = Receipt
    extra = 0

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'bill', 'amount_paid', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('customer__name', 'bill__id', 'transaction_id')
    inlines = [ReceiptInline]

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Receipt)