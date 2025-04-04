from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger('water_billing')

class WaterBillingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A billing system error occurred.'
    default_code = 'billing_error'

class CustomerNotFoundException(WaterBillingException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Customer not found.'
    default_code = 'customer_not_found'

class MeterReadingException(WaterBillingException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid meter reading.'
    default_code = 'invalid_meter_reading'

class PaymentException(WaterBillingException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Payment processing error.'
    default_code = 'payment_error'

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error
        logger.error(f"Error occurred: {exc.__class__.__name__} - {str(exc)}")
        
        # Add custom error handling here
        if isinstance(exc, CustomerNotFoundException):
            response.data['error_type'] = 'customer_not_found'
        elif isinstance(exc, MeterReadingException):
            response.data['error_type'] = 'meter_reading_error'
        elif isinstance(exc, PaymentException):
            response.data['error_type'] = 'payment_error'
        else:
            response.data['error_type'] = 'general_error'

    return response 