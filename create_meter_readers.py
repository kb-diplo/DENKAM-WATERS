import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from account.models import Account


def create_meter_reader(email, first_name, last_name, password):
    """Helper function to create a meter reader account"""
    if Account.objects.filter(email=email).exists():
        print(f"Account with email {email} already exists. Skipping...")
        return
    
    user = Account.objects.create_user(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        role=Account.Role.METER_READER
    )
    print(f"Created meter reader: {user.get_full_name()} ({user.email})")
    return user

# Create meter reader accounts
meter_readers = [
    {
        'email': 'meter.reader1@denkamwaters.com',
        'first_name': 'John',
        'last_name': 'Kamau',
        'password': 'meter123'
    },
    {
        'email': 'meter.reader2@denkamwaters.com',
        'first_name': 'Jane',
        'last_name': 'Wanjiku',
        'password': 'meter123'
    }
]

print("Creating meter reader accounts...")
for reader in meter_readers:
    create_meter_reader(**reader)

print("\nMeter reader accounts created successfully!")
print("You can now log in using the following credentials:")
print("-" * 50)
for reader in meter_readers:
    print(f"Email: {reader['email']}")
    print(f"Password: {reader['password']}")
    print("-" * 50)
