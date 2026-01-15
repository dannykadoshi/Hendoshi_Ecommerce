from django import forms
import re


class PaymentForm(forms.Form):
    """Form for payment information"""
    
    # Card Information
    card_number = forms.CharField(
        max_length=19,
        min_length=13,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '4242 4242 4242 4242',
            'autocomplete': 'cc-number',
        }),
        label='Card Number',
        help_text='Enter 16-digit card number'
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'autocomplete': 'cc-exp',
        }),
        label='Expiry Date',
        help_text='Format: MM/YY'
    )
    
    cvc = forms.CharField(
        max_length=4,
        min_length=3,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'autocomplete': 'cc-csc',
        }),
        label='CVC/CVV',
        help_text='3 or 4 digit security code'
    )
    
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name on Card',
            'autocomplete': 'cc-name',
        }),
        label='Cardholder Name',
    )
    
    billing_address = forms.CharField(
        max_length=250,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123 Main Street',
        }),
        label='Billing Address',
    )
    
    billing_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        }),
        label='Billing City',
    )
    
    billing_postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal Code',
        }),
        label='Billing Postal Code',
    )
    
    COUNTRY_CHOICES = [
        ('', 'Select country'),
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('NL', 'Netherlands'),
        ('BE', 'Belgium'),
        ('CH', 'Switzerland'),
        ('SE', 'Sweden'),
        ('NO', 'Norway'),
        ('DK', 'Denmark'),
        ('FI', 'Finland'),
        ('IE', 'Ireland'),
        ('NZ', 'New Zealand'),
        ('SG', 'Singapore'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('BR', 'Brazil'),
        ('MX', 'Mexico'),
        ('ZA', 'South Africa'),
        ('IN', 'India'),
        ('TH', 'Thailand'),
    ]
    
    billing_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Billing Country',
    )

    same_as_shipping = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Billing address is same as shipping',
    )
    
    def clean_card_number(self):
        """Validate card number format"""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        
        # Check if it's all digits
        if not card_number.isdigit():
            raise forms.ValidationError('Card number must contain only digits.')
        
        # Luhn algorithm check
        if not self.luhn_check(card_number):
            raise forms.ValidationError('Invalid card number.')
        
        return card_number
    
    def clean_expiry_date(self):
        """Validate expiry date format"""
        expiry = self.cleaned_data.get('expiry_date', '')
        
        # Check MM/YY format
        if not re.match(r'^\d{2}/\d{2}$', expiry):
            raise forms.ValidationError('Expiry date must be in MM/YY format.')
        
        month, year = expiry.split('/')
        month = int(month)
        year = int(year)
        
        if not (1 <= month <= 12):
            raise forms.ValidationError('Month must be between 01 and 12.')
        
        # Check if card is expired (simple check, not accounting for current month)
        import datetime
        current_year = datetime.datetime.now().year % 100
        if year < current_year:
            raise forms.ValidationError('Card has expired.')
        
        return expiry
    
    def clean_cvc(self):
        """Validate CVC format"""
        cvc = self.cleaned_data.get('cvc', '')
        
        if not cvc.isdigit():
            raise forms.ValidationError('CVC must contain only digits.')
        
        if not (3 <= len(cvc) <= 4):
            raise forms.ValidationError('CVC must be 3 or 4 digits.')
        
        return cvc
    
    @staticmethod
    def luhn_check(card_number):
        """Validate card number using Luhn algorithm"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10 == 0
