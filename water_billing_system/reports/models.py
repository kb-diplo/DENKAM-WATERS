from django.db import models
from accounts.models import User

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('sales', 'Sales Report'),
        ('payments', 'Payments Report'),
        ('balances', 'Customer Balances Report'),
        ('usage', 'Water Usage Report'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} ({self.start_date} to {self.end_date})"