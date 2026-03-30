from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    """Form for adding/editing user addresses"""

    class Meta:
        model = Address
        fields = [
            'full_name', 'phone', 'address', 'address_line_2',
            'city', 'state_or_county', 'country', 'postal_code', 'is_default'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Full name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Phone number',
            }),
            'address': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Street address',
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Apartment, suite, etc. (optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'City',
            }),
            'state_or_county': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'State/County',
            }),
            'country': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Country',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'profile-form-input',
                'placeholder': 'Postal code',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'phone': 'Phone Number',
            'address': 'Street Address',
            'address_line_2': 'Address Line 2',
            'city': 'City',
            'state_or_county': 'State/County',
            'country': 'Country',
            'postal_code': 'Postal Code',
            'is_default': 'Set as default address',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        address = super().save(commit=False)

        if self.user:
            address.user = self.user

        # If this is being set as default, unset other defaults
        if address.is_default and commit:
            Address.objects.filter(user=address.user, is_default=True).update(is_default=False)

        if commit:
            address.save()

        return address
