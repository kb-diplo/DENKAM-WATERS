# Water Billing System

A web application for water suppliers to manage customer information, meter readings, billing and payments.

## Features

### Supplier-Side
- Customer Management
- Meter Reading Input
- Automated Billing
- Payment Tracking
- Reporting

### Customer-Side
- Account Registration & Login
- Billing History
- Payment History
- Account Management

## Progress

### Week 1
- Set up Django project and apps.
- Designed database schema (ERD).
- Created models for `accounts`, `customers`, `meter_readings`, `billing`, `payments`, and `reports`.
- Implemented basic user authentication.

  ### Week 2  
#### Completed  
**Meter Reading System**  
- Created staff input form with validation  
- Implemented reading history tracking  
- Added role-based access control  

 **Automated Billing**  
- Developed tariff management system  
- Implemented bill calculation based on usage  
- Added status tracking (Pending/Paid/Overdue)  

🛠 **Technical Improvements**  
- Created data migration for existing records  
- Added error handling for invalid readings  
- Implemented success confirmation pages  

#### Testing Coverage  
- Meter reading validation (100%)  
- Bill calculation logic (85%)  
- Authentication flows (90%)  

## Installation  

```bash
git clone https://github.com/your-username/water-billing-system.git
cd water-billing-system
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


