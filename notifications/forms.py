from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """Form for updating notification preferences"""

    class Meta:
        model = NotificationPreference
        fields = [
            'email_notifications_enabled',
            'sale_notifications',
            'restock_notifications',
        ]
        widgets = {
            'email_notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'email_notifications_enabled',
            }),
            'sale_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'sale_notifications',
            }),
            'restock_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'restock_notifications',
            }),
        }
        labels = {
            'email_notifications_enabled': 'Enable all email notifications',
            'sale_notifications': 'Notify me when wishlist items go on sale',
            'restock_notifications': 'Notify me when out-of-stock items are back',
        }
