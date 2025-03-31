from django.contrib import admin
from .models import Customer, Meter

class MeterInline(admin.TabularInline):
    model = Meter
    extra = 1

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'meter_id', 'contact', 'created_at')
    search_fields = ('name', 'meter_id', 'contact')
    inlines = [MeterInline]

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Meter)