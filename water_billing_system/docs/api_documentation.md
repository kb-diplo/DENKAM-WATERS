# Water Billing System API Documentation

## Authentication

### Register a New Customer
```http
POST /api/customers/
Content-Type: application/json

{
    "email": "customer@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "phone": "1234567890",
    "address": "123 Main St",
    "name": "John Doe's Business",
    "contact": "business@example.com",
    "meter_id": "CUSTOM123"
}
```

Response:
```json
{
    "id": 1,
    "name": "John Doe's Business",
    "email": "customer@example.com",
    "message": "Customer registered successfully"
}
```

### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepassword123"
}
```

Response:
```json
{
    "token": "your_auth_token_here"
}
```

## Customer Management

### Get Customer Details
```http
GET /api/customers/
Authorization: Token your_auth_token_here
```

Response:
```json
{
    "id": 1,
    "name": "John Doe's Business",
    "address": "123 Main St",
    "contact": "business@example.com",
    "meter_id": "CUSTOM123",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### Get Customer Bills
```http
GET /api/customers/{customer_id}/bills/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "customer": 1,
        "billing_period": "2024-03",
        "amount": 150.00,
        "status": "unpaid",
        "due_date": "2024-04-15"
    }
]
```

### Get Customer Payments
```http
GET /api/customers/{customer_id}/payments/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "customer": 1,
        "amount": 150.00,
        "payment_date": "2024-03-20",
        "payment_method": "bank_transfer"
    }
]
```

### Get Customer Meter Readings
```http
GET /api/customers/{customer_id}/meter_readings/
Authorization: Token your_auth_token_here
```

Response:
```json
[
    {
        "id": 1,
        "customer": 1,
        "reading_date": "2024-03-20",
        "reading_value": 100.50,
        "consumption": 20.50
    }
]
```

## Testing Steps

1. Register a new customer:
   - Use the registration endpoint to create a new customer account
   - Save the response for the customer ID

2. Login:
   - Use the login endpoint to get an authentication token
   - Save the token for subsequent requests

3. Test Customer Management:
   - Get customer details using the saved token
   - Verify the returned information matches the registration data

4. Test Related Features:
   - Get customer bills
   - Get customer payments
   - Get customer meter readings

Note: All endpoints except registration require authentication using the token received from the login endpoint.

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