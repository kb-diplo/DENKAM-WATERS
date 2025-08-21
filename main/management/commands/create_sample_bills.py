from django.core.management.base import BaseCommand
from main.models import Client, WaterBill, Metric
from account.models import Account
from django.utils import timezone
from decimal import Decimal
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Create sample bills for testing reports page'

    def handle(self, *args, **options):
        # Get existing metric or create one with default values
        metric = Metric.objects.first()
        if not metric:
            metric = Metric.objects.create(
                consumption_rate=Decimal('50.00'),
                penalty_rate=Decimal('10.00')
            )
            self.stdout.write('Created default metric')
        else:
            # Update existing metric if needed
            if metric.consumption_rate == 0 and metric.penalty_rate == 0:
                metric.consumption_rate = Decimal('50.00')
                metric.penalty_rate = Decimal('10.00')
                metric.save()
                self.stdout.write('Updated existing metric with default values')
        
        # Get some clients
        clients = Client.objects.all()[:10]  # Use first 10 clients
        
        if not clients:
            self.stdout.write('No clients found. Please create clients first.')
            return
        
        # Create sample bills
        statuses = ['Paid', 'Pending', 'Overdue']
        admin_user = Account.objects.filter(role=Account.Role.ADMIN).first()
        
        for i, client in enumerate(clients):
            # Create 3 bills per client with different statuses
            for j in range(3):
                status = statuses[j]
                
                # Create bill with random data
                bill = WaterBill.objects.create(
                    created_by=admin_user,
                    name=client,
                    reading=Decimal(str(random.randint(100, 1000))),
                    meter_consumption=Decimal(str(random.randint(10, 100))),
                    status=status,
                    duedate=date.today() + timedelta(days=30),
                    penaltydate=date.today() + timedelta(days=60) if status == 'Overdue' else None,
                    bill=Decimal(str(random.randint(500, 5000))),
                    penalty=Decimal(str(random.randint(0, 500))) if status == 'Overdue' else Decimal('0.00')
                )
                
                self.stdout.write(
                    f'Created {status} bill for {client.name.email}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample bills for {len(clients)} clients')
        )
