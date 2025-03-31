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


