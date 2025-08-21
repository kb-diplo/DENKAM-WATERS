from django.core.management.base import BaseCommand
from account.models import Account
from main.models import Client
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Create 20 sample clients with default password'

    def handle(self, *args, **options):
        # Create 20 sample clients
        for i in range(1, 21):
            # Create user account
            email = f'client{i}@denkamwaters.com'
            first_name = f'Client{i}'
            last_name = f'Customer{i}'
            
            # Check if user already exists
            if Account.objects.filter(email=email).exists():
                self.stdout.write(f'User {email} already exists, skipping...')
                continue
                
            user = Account.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=f'+2547000000{i:02d}',
                role=Account.Role.CUSTOMER,
                password=make_password('customer123'),  # Default password
                is_active=True
            )
            
            # Create client profile
            client = Client.objects.create(
                name=user,
                meter_number=1000 + i,
                address=f'Kahawa Wendani Estate, House {i}',
                status='Connected',
                contact_number=f'+2547000000{i:02d}'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created client {first_name} {last_name} with email {email}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created 20 sample clients')
        )
