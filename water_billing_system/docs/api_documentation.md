# Water Billing System API Documentation

## Authentication

### Get Token
```http
POST /api/token/
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

### Register User
```http
POST /api/accounts/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "address": "123 Main St",
    "role": "customer"
}
```

Response:
```json
{
    "user": {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "1234567890",
        "address": "123 Main St",
        "role": "customer"
    },
    "token": "your_auth_token_here"
}
```

## Customer Management

### Create Meter
```http
POST /api/meters/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "customer": 1,
    "meter_number": "MTR001",
    "initial_reading": 0,
    "installation_date": "2024-03-20"
}
```


### Submit Meter Reading
```http
POST /api/meter-readings/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "customer": 1,
    "meter": 1,
    "reading_value": 1500,
    "reading_date": "2024-04-01"
}
```



### Generate Bill
```http
POST /api/bills/
Authorization: Token your_auth_token_here
Content-Type: application/json

{
    "customer": 1,
    "billing_period": "2024-03-01",
    "current_reading": 1500,
    "previous_reading":1390,
    "rate_per_unit": 2.50
}
```






## Testing Steps

1. Get Authentication Token:
   - Use the token endpoint to get your authentication token
   - Save the token for subsequent requests

2. Register a User:
   - Use the register endpoint to create a new user account
   - Save the user details and token

3. Create a Customer:
   - Use the customer creation endpoint
   - Save the customer ID

4. Create a Meter:
   - Use the meter creation endpoint
   - Save the meter ID

5. Submit a Meter Reading:
   - Use the meter reading endpoint
   - Save the reading ID

6. Generate a Bill:
   - Use the bill generation endpoint
   - Save the bill ID

7. Record a Payment:
   - Use the payment recording endpoint
   - Verify the payment status

Note: All endpoints require authentication using the token received from the token endpoint.

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
    "error_type": "resource_not_found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "A server error occurred.",
    "error_type": "general_error"
}
``` 
