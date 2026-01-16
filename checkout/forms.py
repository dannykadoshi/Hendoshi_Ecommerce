from django import forms
from django.core.exceptions import ValidationError
import re


COUNTRY_CHOICES = [
    ('', '-- Select Country --'),
    # USA
    ('US', 'United States'),
    # European Countries
    ('AT', 'Austria'),
    ('BE', 'Belgium'),
    ('BG', 'Bulgaria'),
    ('HR', 'Croatia'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('EE', 'Estonia'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('DE', 'Germany'),
    ('GR', 'Greece'),
    ('HU', 'Hungary'),
    ('IE', 'Ireland'),
    ('IT', 'Italy'),
    ('LV', 'Latvia'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MT', 'Malta'),
    ('NL', 'Netherlands'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('RO', 'Romania'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('ES', 'Spain'),
    ('SE', 'Sweden'),
    ('GB', 'United Kingdom'),
    ('CH', 'Switzerland'),
    ('NO', 'Norway'),
]

US_STATES = [
    ('', '-- Select State --'),
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
]


class ShippingForm(forms.Form):
    """Form for collecting shipping address information"""
    
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name',
            'aria-label': 'Full name'
        })
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'aria-label': 'Email address'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567',
            'aria-label': 'Phone number'
        })
    )
    
    address = forms.CharField(
        max_length=250,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address',
            'aria-label': 'Street address'
        })
    )
    
    address_line_2 = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartment, suite, etc. (optional)',
            'aria-label': 'Address line 2'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
            'aria-label': 'City'
        })
    )
    
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'aria-label': 'Country'
        })
    )
    
    state_or_county = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/County',
            'aria-label': 'State or County'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal code',
            'aria-label': 'Postal code'
        })
    )
    
    save_to_profile = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'aria-label': 'Save address to profile'
        })
    )
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if not phone:
            raise ValidationError('Phone number is required.')
        
        # Remove common formatting characters
        cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it contains only digits (and optional + at start)
        if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
            raise ValidationError(
                'Enter a valid phone number (10-15 digits, with optional country code).'
            )
        
        return phone
    
    def clean_full_name(self):
        """Validate full name"""
        name = self.cleaned_data.get('full_name', '').strip()
        
        if not name:
            raise ValidationError('Full name is required.')
        
        if len(name.split()) < 2:
            raise ValidationError('Please enter both first and last name.')
        
        return name
    
    def clean_country(self):
        """Validate country selection"""
        country = self.cleaned_data.get('country', '').strip()
        
        if not country:
            raise ValidationError('Please select a country.')
        
        return country
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        country = cleaned_data.get('country')
        state_or_county = cleaned_data.get('state_or_county', '').strip()
        postal_code = cleaned_data.get('postal_code', '').strip()
        
        # Validate state if USA
        if country == 'US' and not state_or_county:
            self.add_error('state_or_county', 'State is required for US addresses.')
        
        # Validate postal code format based on country
        if postal_code:
            if country == 'US':
                if not re.match(r'^\d{5}(-\d{4})?$', postal_code):
                    self.add_error('postal_code', 'Enter a valid US ZIP code (e.g., 12345 or 12345-6789).')
            elif country in ['GB']:
                if not re.match(r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$', postal_code, re.IGNORECASE):
                    self.add_error('postal_code', 'Enter a valid UK postcode.')
        
        return cleaned_data


class ActivateAccountForm(forms.Form):
    """Form for guest users to set their password and activate account"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
        min_length=8,
        help_text='Password must be at least 8 characters long.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        }),
        label='Confirm Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', 'Passwords do not match.')
        
        return cleaned_data
