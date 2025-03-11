from django.db import models

class Report(models.Model):
    report_type = models.CharField(max_length=50)
    generated_date = models.DateField()
    data = models.JSONField()

    def __str__(self):
        return f"{self.report_type} - {self.generated_date}"