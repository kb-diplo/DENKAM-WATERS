# Water Billing System API Documentation

## Authentication

### Register
```http
POST /api/accounts/register/
Content-Type: application/json

{
    "email": "new_user@example.com",
    "password": "secure_password123",
    "password2": "secure_password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "address": "123 Main St",
    "role": "customer"
}
```

Response (201 Created):
```json
{
    "user": {
        "email": "new_user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "role": "customer"
    },
    "token": "your_auth_token"
}
```

### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

Response (200 OK):
```json
{
    "user": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "address": "123 Main St",
        "role": "customer"
    },
    "token": "your_auth_token"
}
```

### Logout
```http
POST /api/accounts/logout/
Authorization: Token your_auth_token
```

Response (204 No Content)

## Customers

### List Customers
```http
GET /api/customers/
Authorization: Token your_auth_token
```

Response:
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "customer1@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "address": "123 Main St"
        }
    ]
}
```

### Create Customer
```http
POST /api/customers/
Authorization: Token your_auth_token
Content-Type: application/json

{
    "email": "new_customer@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "address": "456 Oak Ave"
}
```

## Meter Readings

### Submit Reading
```http
POST /api/meter-readings/
Authorization: Token your_auth_token
Content-Type: application/json

{
    "customer": 1,
    "reading": 1500,
    "reading_date": "2024-04-01"
}
```

## Bills

### List Bills
```http
GET /api/bills/
Authorization: Token your_auth_token
```

### Generate Bill
```http
POST /api/bills/
Authorization: Token your_auth_token
Content-Type: application/json

{
    "customer": 1,
    "period_start": "2024-03-01",
    "period_end": "2024-03-31"
}
```

## Payments

### Record Payment
```http
POST /api/payments/
Authorization: Token your_auth_token
Content-Type: application/json

{
    "bill": 1,
    "amount": 150.00,
    "payment_method": "CASH",
    "payment_date": "2024-04-01"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid input data",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found.",
    "error_type": "customer_not_found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "A server error occurred.",
    "error_type": "general_error"
}
``` 