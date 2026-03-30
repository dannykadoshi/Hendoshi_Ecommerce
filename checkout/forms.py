from django import forms
from django.core.exceptions import ValidationError
import re
from .models import DiscountCode

# ...existing code...

# Restore EditAccountForm for profile editing (must be below all imports and other class definitions)


class EditAccountForm(forms.Form):
    """Form for users to edit their account information"""
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your display name (optional)',
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        from django.contrib.auth.models import User
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Check if username already exists (excluding current user)
        if username and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            self.add_error('username', 'This username is already taken. Please choose another.')

        # Check if email already exists (excluding current user)
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            self.add_error('email', 'This email is already registered. Please use another.')

        return cleaned_data


from django import forms  # noqa: F811,E402
from django.core.exceptions import ValidationError  # noqa: F811,E402
import re  # noqa: F811,E402


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
            'aria-label': 'Full name',
            'autocomplete': 'name'
        })
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'aria-label': 'Email address',
            'autocomplete': 'email'
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567',
            'aria-label': 'Phone number',
            'autocomplete': 'tel'
        })
    )

    address = forms.CharField(
        max_length=250,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address',
            'aria-label': 'Street address',
            'autocomplete': 'address-line1'
        })
    )

    address_line_2 = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartment, suite, etc. (optional)',
            'aria-label': 'Address line 2',
            'autocomplete': 'address-line2'
        })
    )

    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
            'aria-label': 'City',
            'autocomplete': 'address-level2'
        })
    )

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'aria-label': 'Country',
            'autocomplete': 'country'
        })
    )

    state_or_county = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/County',
            'aria-label': 'State or County',
            'autocomplete': 'address-level1'
        })
    )

    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal code',
            'aria-label': 'Postal code',
            'autocomplete': 'postal-code'
        })
    )

    discount_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Discount code (optional)',
            'aria-label': 'Discount code',
            'autocomplete': 'off'
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

    def clean_discount_code(self):
        """Validate discount code"""
        from .models import DiscountCode
        code = self.cleaned_data.get('discount_code', '').strip().upper()

        if not code:
            return None

        try:
            discount_code = DiscountCode.objects.get(code=code)
            is_valid, error_message = discount_code.is_valid()
            if not is_valid:
                raise ValidationError(error_message)
            return discount_code
        except DiscountCode.DoesNotExist:
            raise ValidationError('Invalid discount code.')

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
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
        }),
        help_text='Username will be used to login to your account.'
    )
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
        from django.contrib.auth.models import User
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # Check if username already exists
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', 'This username is already taken. Please choose another.')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', 'Passwords do not match.')

        return cleaned_data


# Form for admin to update order status
class OrderStatusUpdateForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Optional note for status change',
            'rows': 2
        })
    )


class DiscountCodeForm(forms.ModelForm):
    """Form for creating and editing discount codes"""

    class Meta:
        model = DiscountCode
        fields = [
            'code', 'discount_type', 'discount_value', 'minimum_order_value',
            'max_uses', 'max_uses_per_user', 'is_active', 'banner_message', 'banner_button', 'expires_at'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., WELCOME10',
                'style': 'text-transform: uppercase;'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'minimum_order_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_uses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'max_uses_per_user': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'banner_message': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10% OFF your first order with code: WELCOME',
                'maxlength': '200'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper()
        if not code:
            raise forms.ValidationError("Discount code is required.")

        # Check for uniqueness (excluding current instance if editing)
        qs = DiscountCode.objects.filter(code=code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A discount code with this name already exists.")

        return code

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')

        if discount_type == 'percentage' and discount_value and discount_value > 100:
            raise forms.ValidationError("Percentage discount cannot exceed 100%.")

        return cleaned_data


class ShippingRateForm(forms.ModelForm):
    """Form for creating/editing ShippingRate objects via the frontend admin views."""
    class Meta:
        from .models import ShippingRate
        model = ShippingRate
        fields = ['name', 'price', 'free_over', 'estimated_delivery', 'is_active', 'is_standard']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Standard'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'free_over': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_delivery': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5-7 business days'}),  # noqa: E501
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_standard': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
