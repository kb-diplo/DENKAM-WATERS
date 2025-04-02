# Denkam Waters API Documentation

## Authentication
Use token authentication for API requests:


## Endpoints

### Customers
- `GET /api/customers/` - List all customers
- `POST /api/customers/` - Create new customer
- `GET /api/customers/{id}/` - Retrieve customer details
- `PUT /api/customers/{id}/` - Update customer
- `DELETE /api/customers/{id}/` - Delete customer

### Meter Readings
- `GET /api/meter-readings/` - List all readings
- `POST /api/meter-readings/` - Create new reading
- `GET /api/meter-readings/{id}/` - Retrieve reading details

### Bills
- `GET /api/bills/` - List all bills
- `POST /api/bills/` - Create new bill
- `GET /api/bills/{id}/` - Retrieve bill details

### Payments
- `GET /api/payments/` - List all payments
- `POST /api/payments/` - Create new payment
- `GET /api/payments/{id}/` - Retrieve payment details

## Example Requests

### Create Customer
```json
POST /api/customers/
{
    "name": "John Doe",
    "address": "123 Main St",
    "contact": "+254712345678",
    "meter_id": "M12345"
}