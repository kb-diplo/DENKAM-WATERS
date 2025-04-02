# Denkam Waters Billing System

A comprehensive water billing system with manual meter reading and customer portal.

## Features

### Supplier-Side Functionality
- **Customer Management**: Add, edit, view, and deactivate customers
- **Meter Reading**: Manual input with validation checks
- **Billing**: Automatic bill calculation based on tariffs
- **Payments**: Record and track customer payments
- **Reporting**: Generate sales, payments, and customer balance reports
- **User Management**: Create staff accounts with different permission levels

### Customer Portal
- **Account Dashboard**: View bills and payment history
- **Usage Tracking**: Monitor water consumption
- **Document Access**: Download invoices and receipts
- **Profile Management**: Update personal information

## Technologies Used
- Python 3.x
- Django 4.x
- PostgreSQL (production) / SQLite (development)
- Bootstrap 5
- Django REST Framework
- xhtml2pdf

## Installation

### Requirements
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/kb-diplo/DENKAM-WATERS.git
   cd water_billing_system
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   copy .env.example .env
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create admin user:
   ```bash
   python manage.py createsuperuser
   ```

7. Load initial data (optional):
   ```bash
   python manage.py load_initial_data
   ```

8. Run development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

### Customers
- `GET /api/customers/` - List all customers
- `POST /api/customers/` - Create new customer

### Meter Readings
- `POST /api/meter-readings/` - Submit new reading

### Bills
- `GET /api/bills/` - List all bills
- `POST /api/bills/` - Generate new bill

### Payments
- `POST /api/payments/` - Record payment

## Project Structure
```
denkam-waters/
├── accounts/          # User authentication
├── billing/           # Billing and invoicing
├── customers/         # Customer management
├── meter_readings/    # Meter reading handling
├── payments/          # Payment processing
├── reports/           # Reporting system
├── static/            # Static files
└── templates/         # HTML templates
```

## Running Tests
```bash
python manage.py test
```

## Deployment

### Heroku Deployment
1. Install Heroku CLI and login:
   ```bash
   npm install -g heroku
   heroku login
   ```

2. Create a Heroku app:
   ```bash
   heroku create water_billing_system
   ```

3. Add PostgreSQL add-on:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. Configure environment variables:
   ```bash
   heroku config:set DEBUG=False SECRET_KEY=your_secret_key
   ```

5. Add a Procfile to your project root:
   ```
   web: gunicorn your_project_name.wsgi --log-file -
   ```

6. Install additional dependencies:
   ```bash
   pip install gunicorn dj-database-url psycopg2-binary
   pip freeze > requirements.txt
   ```

7. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

8. Run migrations on Heroku:
   ```bash
   heroku run python manage.py migrate
   ```

9. Create a superuser on Heroku:
   ```bash
   heroku run python manage.py createsuperuser
   ```

### Docker
```bash
docker-compose up -d --build
```

## License
MIT License

## Contact
Lawrence Mbugua - tingzlarry@gmail.com
