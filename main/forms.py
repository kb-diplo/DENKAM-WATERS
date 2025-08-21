from django import forms
from .models import *
from django import forms
from django.forms import ModelForm
from decimal import Decimal


class BillForm(forms.ModelForm):
    # Custom field for client name editing
    client_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Name'}),
        label='Client Name'
    )
    
    class Meta:
        model = WaterBill
        fields = ['name', 'meter_consumption', 'status', 'duedate', 'penaltydate']
        exclude = ['penalty', 'bill',]
        widgets = {
            'name': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Name' }),
            'meter_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder':'0.00' }),
            'status': forms.Select(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Pay Status' }),
            'duedate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Due Date' }),
            'penaltydate': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder':'Penalty Date' }),
        }
    
    def __init__(self, *args, **kwargs):
        super(BillForm, self).__init__(*args, **kwargs)
        # If we're editing an existing bill, populate the client_name field
        if self.instance and self.instance.pk:
            self.fields['client_name'].initial = self.instance.name.get_full_name()
            # Hide the name field as we'll use client_name instead
            self.fields['name'].widget = forms.HiddenInput()


class ClientUpdateForm(forms.ModelForm):
    """
    Form for updating client information.
    This form is used by admins to update client details.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        }),
        help_text='Client email address.'
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': '+254...',
            'autocomplete': 'tel'
        }),
        help_text='Format: +254...',
        label='Phone Number'
    )

    class Meta:
        model = Client
        fields = ['meter_number', 'middle_name', 'contact_number', 'address', 'status', 'assigned_meter_reader']
        widgets = {
            'meter_number': forms.NumberInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Meter Number',
                'min': '1'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Middle Name (Optional)'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': '+254...',
                'autocomplete': 'tel'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control form-control-user',
                'rows': 2,
                'placeholder': 'Physical Address',
                'autocomplete': 'street-address'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-control-user custom-select',
            }),
            'assigned_meter_reader': forms.Select(attrs={
                'class': 'form-control form-control-user custom-select',
            }),
        }
        help_texts = {
            'meter_number': 'Unique meter number for the client',
            'assigned_meter_reader': 'Meter reader responsible for this client',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'name'):
            self.fields['email'].initial = self.instance.name.email
            self.fields['phone_number'].initial = self.instance.name.phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Account.objects.filter(email=email).exclude(pk=self.instance.name_id).exists():
            raise forms.ValidationError('This email is already in use by another account.')
        return email

    def save(self, commit=True):
        client = super().save(commit=False)
        
        # Update the related Account model
        if hasattr(client, 'name'):
            client.name.email = self.cleaned_data['email']
            client.name.phone_number = self.cleaned_data['phone_number']
            if commit:
                client.name.save()
        
        if commit:
            client.save()
            self.save_m2m()
            
        return client

class ClientForm(forms.ModelForm):
    """
    Form for creating a new client with email and password.
    This form creates both an Account and a related Client profile.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Email Address',
            'autocomplete': 'new-email'
        }),
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long.',
        min_length=8
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': '+254...',
            'autocomplete': 'tel'
        }),
        help_text='Format: +254...',
        label='Phone Number'
    )

    class Meta:
        model = Client
        fields = ['meter_number', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'middle_name', 'contact_number', 'address', 'status', 'assigned_meter_reader']
        widgets = {
            'meter_number': forms.NumberInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Meter Number',
                'min': '1',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'client@example.com'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Enter password'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Middle Name (Optional)'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': '+254...',
                'autocomplete': 'tel'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control form-control-user',
                'rows': 2,
                'placeholder': 'Physical Address',
                'autocomplete': 'street-address',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-control-user custom-select',
                'required': True
            }),
            'assigned_meter_reader': forms.Select(attrs={
                'class': 'form-control form-control-user custom-select',
                'required': False
            }),
        }
        help_texts = {
            'meter_number': 'Unique meter number for the client',
            'assigned_meter_reader': 'Meter reader responsible for this client (optional)',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different one.")
        return email

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
        
    def clean_meter_number(self):
        meter_number = self.cleaned_data.get('meter_number')
        if meter_number and Client.objects.filter(meter_number=meter_number).exists():
            raise forms.ValidationError("A client with this meter number already exists.")
        return meter_number

    def save(self, commit=True):
        # Create the user account first
        user = Account.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone_number=self.cleaned_data.get('phone_number', ''),
            role=Account.Role.CUSTOMER
        )
        
        # Create the client profile
        client = super().save(commit=False)
        client.name = user  # Link the client to the user account
        
        # Set the assigned meter reader if provided
        if 'assigned_meter_reader' in self.cleaned_data:
            client.assigned_meter_reader = self.cleaned_data['assigned_meter_reader']
        
        if commit:
            client.save()
            self.save_m2m()
            
        return client

    class Meta:
        model = Client
        fields = ['meter_number', 'first_name', 'middle_name', 'last_name', 'email', 'password', 'contact_number', 'address', 'status']
        widgets = {
            'meter_number': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder': '0000000'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kahawa Estate'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class UpdateProfileForm(forms.ModelForm):
    """
    Form for updating user profile information including password change.
    """
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Leave blank to keep current password',
            'autocomplete': 'current-password'
        }),
        label='Current Password',
        help_text='Enter your current password to change it.'
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        }),
        label='New Password',
        min_length=8,
        help_text='Leave blank to keep current password.'
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
        label='Confirm New Password'
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'First Name',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Last Name',
                'autocomplete': 'family-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Email Address',
                'autocomplete': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Phone Number (e.g. +254...)',
                'autocomplete': 'tel'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email field required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use by another account.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')

        # Check if new password is provided without current password
        if new_password and not current_password:
            self.add_error('current_password', 'Please enter your current password to change it.')
        
        # Check if current password is correct when changing password
        if current_password and not self.instance.check_password(current_password):
            self.add_error('current_password', 'Incorrect current password.')
        
        # Check if new passwords match
        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Update password if a new one was provided
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        
        return user


class MetricsForm(forms.ModelForm):
    class Meta:
        model = Metric
        fields = '__all__'
        widgets = {
            'consumption_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder':'0.00' }),
            'penalty_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder':'0.00' })
        }

class AddBillForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().order_by('name__first_name', 'name__last_name'),
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'id': 'client-select',
            'style': 'width: 100%'
        }),
        label='Select Client',
        required=True
    )
    
    previous_reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'id': 'previous-reading'
        }),
        label='Previous Reading'
    )
    
    current_reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'id': 'current-reading',
            'placeholder': 'Enter current meter reading'
        }),
        label='Current Reading',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial queryset to only include active clients
        self.fields['client'].queryset = Client.objects.filter(
            name__is_active=True
        ).order_by('name__first_name', 'name__last_name')


class MeterReadingForm(forms.ModelForm):
    reading = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Current Reading',
        help_text='Enter the current meter reading in cubic meters (m³)'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False,
        label='Notes',
        help_text='Optional: Any additional notes about this reading'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reading'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Enter meter reading (e.g., 123.45)'
        })
        self.fields['notes'].widget.attrs.update({'class': 'form-control'})


class PaymentRecordForm(forms.Form):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
    ]
    
    bill = forms.ModelChoiceField(
        queryset=WaterBill.objects.filter(status='Pending').select_related('name__name'),
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'id': 'bill-select',
            'required': True
        }),
        label='Select Bill',
        empty_label='Select a bill to pay',
        help_text='Only pending bills are shown'
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'payment-method',
            'required': True
        }),
        label='Payment Method'
    )
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01',
            'required': True,
            'placeholder': '0.00',
            'id': 'payment-amount'
        }),
        label='Amount (KES)',
        help_text='Enter the payment amount'
    )
    
    reference_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. MPESA123, BANK456, CASH789',
            'required': True
        }),
        label='Payment Reference',
        help_text='Enter the payment reference number or code'
    )
    
    payment_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'id': 'payment-date'
        }),
        label='Payment Date',
        help_text='Select the date and time when payment was made (leave blank for current date/time)'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Additional notes about this payment (optional)'
        }),
        label='Notes',
        help_text='Any additional information about this payment'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the queryset to show client name and bill amount in the dropdown
        self.fields['bill'].label_from_instance = self.bill_label_from_instance
    
    @staticmethod
    def bill_label_from_instance(obj):
        client_name = obj.name.name.get_full_name()
        # Use the bill's compute_bill method for accurate calculation
        amount = obj.compute_bill() if hasattr(obj, 'compute_bill') else (obj.bill or 0)
        return f"{client_name} - Bill #{obj.id} - KSh {amount:,.2f}"
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        bill = self.cleaned_data.get('bill')
        
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
            
        if bill:
            # Calculate the expected bill amount using the bill's method
            bill_amount = bill.compute_bill() if hasattr(bill, 'compute_bill') else (bill.bill or 0)
            
            # Allow partial payments and overpayments, just warn if amount seems unusual
            if amount <= 0:
                raise forms.ValidationError('Payment amount must be greater than zero.')
            
            # Optional: warn if payment is significantly different from bill amount
            # This is just a warning, not a blocking validation
            if bill_amount > 0 and abs(amount - Decimal(str(bill_amount))) > (Decimal(str(bill_amount)) * Decimal('0.1')):  # 10% difference
                # This is just informational, don't block the payment
                pass
                
        return amount