from django.contrib import admin
from .models import MeterReading

class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ('meter', 'reading_date', 'reading_value', 'recorded_by')
    list_filter = ('meter__customer', 'reading_date')
    search_fields = ('meter__customer__name', 'meter__meter_id')
    date_hierarchy = 'reading_date'

admin.site.register(MeterReading, MeterReadingAdmin)