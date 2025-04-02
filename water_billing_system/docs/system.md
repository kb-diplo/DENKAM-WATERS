# Denkam Waters Billing System Documentation

## System Overview
The Denkam Waters Billing System manages water billing operations including:
- Customer management
- Meter reading collection
- Bill generation
- Payment processing
- Reporting

## User Roles
1. **Admin**: Full system access
2. **Supplier**: Customer and billing management
3. **Meter Reader**: Only meter reading input
4. **Customer**: Self-service portal access

## Workflow
1. Staff adds customer and installs meter
2. Meter reader records readings
3. System generates bills automatically
4. Customer makes payment
5. Staff records payment
6. System updates bill status

## Installation
1. Clone repository
2. Create virtual environment
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Run server: `python manage.py runserver`