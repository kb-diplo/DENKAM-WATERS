# Denkam Waters Billing System

A comprehensive water billing system with manual meter reading and customer portal for Denkam Waters.

User Authentication System with different roles (admin, supplier, meter reader, customer)

Customer Management for tracking customer information and meters

Meter Reading System for manual input of water consumption data

Automated Billing with configurable tariffs and invoice generation

Payment Processing with receipt generation

Comprehensive Reporting for sales, payments, and customer balances

Customer Portal for self-service access to billing information

PDF Generation for invoices and receipts

Responsive UI built with Bootstrap 5

## Features

### Supplier-Side Functionality
- **Customer Management**: Add, edit, and deactivate customers
- **Meter Reading Input**: Manual entry of meter readings with validation
- **Automated Billing**: Generate bills based on meter readings and tariffs
- **Payment Tracking**: Record payments and reconcile with outstanding bills
- **Reporting**: Generate sales, payments, and customer balances reports
- **User Management**: Create staff accounts with role-based permissions (admin, supplier, meter reader)

### Customer-Side Functionality
- **Self-Service Portal**: View bills and payment history
- **Usage Tracking**: Monitor water consumption over time
- **Account Management**: Update personal information and settings
- **Document Access**: Download invoices and payment receipts

## Technologies Used
- **Backend**: Python 3.x, Django 4.x
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **PDF Generation**: xhtml2pdf
- **Authentication**: Django's built-in auth with custom user model
- **Deployment**: Docker, Nginx, Gunicorn (optional)

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional for production)
- pip

### Setup Instructions

1. **Clone the repository**:
   
```bash
git clone https://github.com/your-username/water-billing-system.git
cd water-billing-system

**Create and activate virtual environment:**

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install dependencies:

```bash
pip install -r requirements.txt
Configuration

Create .env file:
'''ini
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

Run migrations:
```bash
python manage.py migrate
Create admin user:

```bash
python manage.py createsuperuser
Load sample data:

```bash
python manage.py load_initial_data
Usage
Accessing the System
Admin Dashboard: http://localhost:8000/admin

Customer Portal: http://localhost:8000

API Base URL: http://localhost:8000/api/

Test Accounts
Role	Username	Password
Admin	admin	admin123
Supplier	supplier	supplier123
Customer	customer1	customer123
API Documentation
Authentication
http
Copy
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
Available Endpoints
Endpoint	Method	Description
/api/customers/	GET	List customers
/api/meter-readings/	POST	Submit reading
/api/bills/	POST	Generate bill
/api/reports/sales/	GET	Sales report
Testing
Run unit tests:

```bash
python manage.py test
Manual test cases:

User registration flow

Meter reading submission

Bill generation process

Payment recording

Troubleshooting
Common Issues:

Import Errors

```bash
pip install -r requirements.txt
Database Issues

```bash
python manage.py makemigrations
python manage.py migrate
Static Files Not Loading

```bash
python manage.py collectstatic
Deployment
Production Setup
Configure PostgreSQL in .env:

'''ini
DATABASE_URL=postgres://user:password@localhost:5432/denkam_waters
Set up Gunicorn:

```bash
pip install gunicorn
gunicorn water_billing_system.wsgi:application
Configure Nginx as reverse proxy

Docker Deployment
```bash
docker-compose up -d
License
This project is licensed under the MIT License - see LICENSE file for details.

Project Maintainer: [LAWRENCE MBUGUA NJUGUNA]
Contact: tingzlarry@gmail.com