from django.contrib import admin
from .models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'start_date', 'end_date', 'created_at')
    list_filter = ('report_type', 'created_at')
    date_hierarchy = 'created_at'

admin.site.register(Report, ReportAdmin)