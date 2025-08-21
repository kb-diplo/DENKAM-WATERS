from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
import json
import base64
import logging
import datetime
from django.conf import settings
from .models import MpesaPayment
from main.models import WaterBill

logger = logging.getLogger(__name__)

def get_mpesa_access_token():
    """Get M-Pesa OAuth access token"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = f'{settings.MPESA_API_URL}/oauth/v1/generate?grant_type=client_credentials'

    if not consumer_key or not consumer_secret:
        logger.error("MPESA_CONSUMER_KEY or MPESA_CONSUMER_SECRET not configured in settings.")
        return None

    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret), timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        if 'access_token' in token_data:
            logger.info("Successfully obtained M-Pesa access token.")
            return token_data['access_token']
        else:
            logger.error(f"Access token not found in response: {token_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting M-Pesa access token: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response when getting access token: {e}")
        return None

def generate_password():
    """Generate M-Pesa API password using the passkey"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password_string = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password_bytes = password_string.encode('ascii')
    password = base64.b64encode(password_bytes).decode('utf-8')
    return password, timestamp

@login_required
def initiate_stk_push(request, bill_id):
    """Initiate STK push payment for a bill"""
    bill = get_object_or_404(WaterBill, id=bill_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        # Format phone number to 2547XXXXXXXX
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]
            
        if not phone_number.isdigit() or len(phone_number) != 12:
            messages.error(request, 'Please enter a valid phone number (e.g., 07XXXXXXXX or 2547XXXXXXXX)')
            return redirect('main:bill_detail', bill_id=bill_id)
            
        # Get access token
        access_token = get_mpesa_access_token()
        if not access_token:
            messages.error(request, 'Failed to connect to payment service. Please try again later.')
            return redirect('main:bill_detail', bill_id=bill_id)
            
        # Generate password and timestamp
        password, timestamp = generate_password()
        
        # Prepare STK push payload
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': settings.MPESA_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(bill.amount),
            'PartyA': phone_number,
            'PartyB': settings.MPESA_SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': settings.MPESA_CALLBACK_URL,
            'AccountReference': f"WATER{str(bill.id).zfill(6)}",
            'TransactionDesc': f"Water Bill Payment - {bill.id}"
        }
        
        try:
            # Send STK push request
            response = requests.post(
                f"{settings.MPESA_API_URL}/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Check if request was successful
            if 'ResponseCode' in response_data and response_data['ResponseCode'] == '0':
                # Create payment record
                MpesaPayment.objects.create(
                    bill=bill,
                    phone_number=phone_number,
                    amount=bill.amount,
                    transaction_id=response_data.get('CheckoutRequestID'),
                    is_successful=False
                )
                messages.success(request, 'Payment request sent successfully! Please check your phone to complete the payment.')
            else:
                error_message = response_data.get('errorMessage', 'Failed to initiate payment. Please try again.')
                messages.error(request, f'Payment failed: {error_message}')
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating STK push: {str(e)}")
            messages.error(request, 'Failed to connect to payment service. Please try again later.')
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messages.error(request, 'An unexpected error occurred. Please try again.')
            
        return redirect('main:bill_detail', bill_id=bill_id)
    
    # If not POST, show the payment form
    context = {
        'bill': bill,
        'title': 'Pay with M-Pesa'
    }
    return render(request, 'mpesa/initiate_payment.html', context)

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa STK push callback"""
    if request.method != 'POST':
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Method not allowed'}, status=405)
    
    try:
        # Log the raw request body for debugging
        raw_body = request.body.decode('utf-8')
        logger.info(f"Received M-Pesa callback: {raw_body}")
        
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in M-Pesa callback: {e}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'}, status=400)
        
        # Safely extract callback data with proper error handling
        callback_data = data.get('Body', {}).get('stkCallback', {})
        result_code = callback_data.get('ResultCode')
        checkout_request_id = callback_data.get('CheckoutRequestID')
        
        if not checkout_request_id:
            logger.error("No CheckoutRequestID in callback data")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Missing CheckoutRequestID'}, status=400)
        
        # Try to get the payment record
        try:
            payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
        except MpesaPayment.DoesNotExist:
            logger.error(f"Payment with CheckoutRequestID {checkout_request_id} not found")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Payment not found'}, status=404)
        
        # Process based on result code
        if result_code == 0:
            # Payment was successful
            payment_metadata = next(
                (item for item in callback_data.get('CallbackMetadata', {}).get('Item', []) 
                 if item.get('Name') == 'MpesaReceiptNumber'),
                {}
            )
            
            receipt_number = payment_metadata.get('Value')
            
            # Update payment record
            payment.is_successful = True
            payment.status = 'completed'
            payment.receipt_number = receipt_number
            payment.transaction_id = receipt_number or checkout_request_id
            payment.raw_callback_data = data
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update bill status
            bill = payment.bill
            bill.status = 'Paid'
            bill.payment_date = timezone.now()
            bill.save()
            
            logger.info(f"Payment {checkout_request_id} marked as successful. Receipt: {receipt_number}")
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Request processed successfully'})
        else:
            # Payment failed
            error_message = callback_data.get('ResultDesc', 'Payment failed')
            payment.status = 'failed'
            payment.is_successful = False
            payment.notes = f"Payment failed: {error_message}"
            payment.raw_callback_data = data
            payment.save()
            
            logger.error(f"Payment {checkout_request_id} failed: {error_message}")
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Request processed successfully'})
            
    except Exception as e:
        logger.error(f"Unexpected error in mpesa_callback: {str(e)}", exc_info=True)
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Internal server error'}, status=500)
