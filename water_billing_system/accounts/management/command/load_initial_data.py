from django.core.management.base import BaseCommand
from accounts.models import User
from customers.models import Customer, Meter
from billing.models import Tariff

class Command(BaseCommand):
    help = 'Load initial data for Denkam Waters'
    
    def handle(self, *args, **options):
        self.stdout.write("Loading initial data...")
        
        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@denkamwaters.com',
            password='admin123',
            role='admin'
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        
        # Create supplier user
        supplier = User.objects.create_user(
            username='supplier',
            email='supplier@denkamwaters.com',
            password='supplier123',
            role='supplier'
        )
        self.stdout.write(self.style.SUCCESS(f'Created supplier user: {supplier.username}'))
        
        # Create meter reader user
        meter_reader = User.objects.create_user(
            username='meter_reader',
            email='meter_reader@denkamwaters.com',
            password='meter123',
            role='meter_reader'
        )
        self.stdout.write(self.style.SUCCESS(f'Created meter reader user: {meter_reader.username}'))
        
        # Create sample customer
        customer_user = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='customer123',
            role='customer'
        )
        
        customer = Customer.objects.create(
            user=customer_user,
            name='John Doe',
            address='123 Main Street, Nairobi',
            contact='+254712345678',
            meter_id='M12345'
        )
        self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.name}'))
        
        # Create meter for customer
        meter = Meter.objects.create(
            customer=customer,
            installation_date='2023-01-01',
            last_reading=0
        )
        self.stdout.write(self.style.SUCCESS(f'Created meter: {meter.id} for {customer.name}'))
        
        # Create tariff
        tariff = Tariff.objects.create(
            name='Standard Residential',
            rate_per_unit=50.00,
            fixed_charge=200.00,
            description='Standard tariff for residential customers'
        )
        self.stdout.write(self.style.SUCCESS(f'Created tariff: {tariff.name} @ KES {tariff.rate_per_unit}/unit'))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))