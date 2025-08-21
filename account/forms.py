from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core import validators
from .models import Account
from main.models import Client


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Account
        fields = ('first_name', 'last_name', 'email')


class CustomerRegistrationForm(RegistrationForm):
    """Form for clients to register themselves, or for meter readers to register them."""
    pass


class AdminUserCreationForm(forms.Form):
    """
    A unified form for administrators to create new users (both Customers and
    Meter Readers). It dynamically requires client-specific fields based on the
    selected role.
    """
    ROLE_CHOICES = (
        (Account.Role.CUSTOMER, 'Customer'),
        (Account.Role.METER_READER, 'Meter Reader'),
    )

    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254...'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Kahawa Estate'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        contact_number = cleaned_data.get('contact_number')
        address = cleaned_data.get('address')

        if role == Account.Role.CUSTOMER:
            if not contact_number:
                self.add_error('contact_number', 'This field is required for customers.')
            if not address:
                self.add_error('address', 'This field is required for customers.')
        return cleaned_data



class FormSettings(forms.ModelForm):
   def __init__(self, *args, **kwargs):
      super(FormSettings, self).__init__(*args, **kwargs)
      for field in self.visible_fields():
         field.field.widget.attrs['class'] = 'form-control form-control-user'


class RegistrationForm(FormSettings):
   def save(self, commit=True):
      user = super(RegistrationForm, self).save(commit=False)
      password = self.cleaned_data.get("password")
      if password:
         user.set_password(password)
      if commit:
         user.save()
      return user

   def __init__(self, *args, **kwargs):
      super(RegistrationForm, self).__init__(*args, **kwargs)
      if kwargs.get('instance'):
         instance = kwargs.get('instance').__dict__
         self.fields['password'].required = False
         for field in RegistrationForm.Meta.fields:
            self.fields[field].initial = instance.get(field)
         if self.instance.pk is not None:
            self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
         else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

   def clean_email(self, *args, **kwargs):
      formEmail = self.cleaned_data['email'].lower()

      # domain = formEmail.split('@')[1]
      # domain_list = ["ssct.edu.ph"]
      # if domain not in domain_list:
      #    raise forms.ValidationError("Please enter ssct gsuite email")
      if self.instance.pk is None: 
         if Account.objects.filter(email=formEmail).exists():
               raise forms.ValidationError(
                  "The given email is already registered")
      else:  # Update
         dbEmail = self.Meta.model.objects.get(
               id=self.instance.pk).email.lower()
         if dbEmail != formEmail:  # There has been changes
               if Account.objects.filter(email=formEmail).exists():
                  raise forms.ValidationError(
                     "The given email is already registered")
      return formEmail

   class Meta:
      model = Account
      fields = ['last_name', 'first_name', 'email', 'password',]
      widgets = {
      'last_name':forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Last name' }),
      'first_name':forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'First Name' }),
      'password': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control', 'placeholder':'Password' }),
      'email': forms.TextInput(attrs={'type': 'email', 'class': 'form-control', 'placeholder':'Email' }),
   }


class UpdateProfileForm(FormSettings):
   phone_number = forms.CharField(max_length=20, required=False)

   def save(self, commit=True):
      user = super(UpdateProfileForm, self).save(commit=False)
      password = self.cleaned_data.get("password")
      if password:
         user.set_password(password)
      if commit:
         user.save()
      return user

   def __init__(self, *args, **kwargs):
      super(UpdateProfileForm, self).__init__(*args, **kwargs)
      if kwargs.get('instance'):
         instance = kwargs.get('instance').__dict__
         self.fields['password'].required = False
         for field in UpdateProfileForm.Meta.fields:
            self.fields[field].initial = instance.get(field)
         if self.instance.pk is not None:
            self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
         else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

   def clean_email(self, *args, **kwargs):
      formEmail = self.cleaned_data['email'].lower()

      # domain = formEmail.split('@')[1]
      # domain_list = ["ssct.edu.ph"]
      # if domain not in domain_list:
      #    raise forms.ValidationError("Please enter ssct gsuite email")
      if self.instance.pk is None: 
         if Account.objects.filter(email=formEmail).exists():
               raise forms.ValidationError(
                  "The given email is already registered")
      else:  # Update
         dbEmail = self.Meta.model.objects.get(
               id=self.instance.pk).email.lower()
         if dbEmail != formEmail:  # There has been changes
               if Account.objects.filter(email=formEmail).exists():
                  raise forms.ValidationError(
                     "The given email is already registered")
      return formEmail

   class Meta:
      model = Account
      exclude = ['last_name', 'first_name', 'email', 'department']
      fields = ['phone_number', 'password',]
      widgets = {
      'password': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control', 'placeholder':'Password' }),
   }



class UpdateUserForm(FormSettings):
   def save(self, commit=True):
      user = super(UpdateUserForm, self).save(commit=False)
      password = self.cleaned_data.get("password")
      if password:
         user.set_password(password)
      if commit:
         user.save()
      return user

   def __init__(self, *args, **kwargs):
      super(UpdateUserForm, self).__init__(*args, **kwargs)
      if kwargs.get('instance'):
         instance = kwargs.get('instance').__dict__
         self.fields['password'].required = False
         for field in UpdateUserForm.Meta.fields:
            self.fields[field].initial = instance.get(field)
         if self.instance.pk is not None:
            self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
         else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

   def clean_email(self, *args, **kwargs):
      formEmail = self.cleaned_data['email'].lower()

      if self.instance.pk is None: 
         if Account.objects.filter(email=formEmail).exists():
               raise forms.ValidationError(
                  "The given email is already registered")
      else:  # Update
         dbEmail = self.Meta.model.objects.get(
               id=self.instance.pk).email.lower()
         if dbEmail != formEmail:  # There has been changes
               if Account.objects.filter(email=formEmail).exists():
                  raise forms.ValidationError(
                     "The given email is already registered")
      return formEmail

   class Meta:
      model = Account
      exclude = ['verified',]
      fields = ['last_name', 'first_name', 'email', 'password']
      widgets = {
      'last_name':forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'Last name' }),
      'first_name':forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder':'First Name' }),
      'email': forms.TextInput(attrs={'type': 'email', 'class': 'form-control', 'placeholder':'Email' }),
      'password': forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control', 'placeholder':'Password' }),
   }



class CustomerRegistrationForm(forms.ModelForm):
    """Form for admins to register new client accounts with enhanced styling."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long.',
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )
    contact_number = forms.CharField(
        max_length=13, 
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Contact Number (e.g., +254...)'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-user',
            'rows': 3, 
            'placeholder': 'Full physical address...'
        })
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'contact_number', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'First Name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Last Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Email Address',
                'required': True
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = Account.Role.CUSTOMER
        user.verified = True  # Admin-created users are automatically verified
        if commit:
            user.save()
            # Create client profile
            Client.objects.create(
                name=user,
                contact_number=self.cleaned_data.get('contact_number'),
                address=self.cleaned_data.get('address'),
                status='Active'  # Changed from 'Pending' to 'Active' as admin is creating this
            )
        return user


class MeterReaderRegistrationForm(forms.ModelForm):
    """
    Form for admins to register new meter readers with enhanced validation and styling.
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        help_text='Password must be at least 8 characters long and include numbers and special characters.',
        min_length=8,
        validators=[
            validators.RegexValidator(
                regex='^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message='Password must contain at least one letter, one number, and one special character.',
                code='invalid_password'
            ),
        ]
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'First Name',
                'required': True,
                'autofocus': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Last Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control form-control-user',
                'placeholder': 'Phone Number (e.g., +254...)',
                'required': True
            }),
        }
        help_texts = {
            'email': 'A valid email address is required for account verification and notifications.',
            'phone_number': 'Please include country code (e.g., +254 for Kenya).',
        }
        error_messages = {
            'first_name': {
                'required': 'First name is required.',
                'max_length': 'Name is too long.'
            },
            'last_name': {
                'required': 'Last name is required.',
                'max_length': 'Name is too long.'
            },
            'email': {
                'required': 'Email is required.',
                'invalid': 'Enter a valid email address.'
            },
            'phone_number': {
                'required': 'Phone number is required.',
                'invalid': 'Enter a valid phone number with country code.'
            }
        }

    def __init__(self, *args, **kwargs):
        super(MeterReaderRegistrationForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control form-control-user'
            
            # Add required attribute for client-side validation
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered. Please use a different email address.",
                code='duplicate_email'
            )
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Basic phone number validation (can be enhanced with a proper phone number library)
        if not phone_number.startswith('+'):
            raise forms.ValidationError("Please include the country code (e.g., +254...)")
        if not phone_number[1:].isdigit():
            raise forms.ValidationError("Phone number should only contain numbers after the country code.")
        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The two password fields didn't match. Please enter the same password in both fields.",
                code='password_mismatch'
            )
        return password2
        
    def save(self, commit=True):
        """
        Save the meter reader account with the provided password and role.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = Account.Role.METER_READER
        user.is_staff = True  # Give staff access
        user.verified = True  # Admin-created users are automatically verified
        
        if commit:
            user.save()
            # Additional processing can be added here if needed
            
        return user
        return user

class AdminRegistrationForm(RegistrationForm):

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Account.Role.ADMIN
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
        return user


class MeterReaderClientCreationForm(forms.Form):
    """Form for meter readers and admins to create new client accounts."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=True
    )
    contact_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254...'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Kahawa Estate'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email