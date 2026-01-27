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
            'cart_abandonment_notifications',
            'vault_photo_notifications',
            'vault_featured_notifications',
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
            'cart_abandonment_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'cart_abandonment_notifications',
            }),
            'vault_photo_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'vault_photo_notifications',
            }),
            'vault_featured_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'vault_featured_notifications',
            }),
        }
        labels = {
            'email_notifications_enabled': 'Enable all email notifications',
            'sale_notifications': 'Notify me when wishlist items go on sale',
            'restock_notifications': 'Notify me when out-of-stock items are back',
            'cart_abandonment_notifications': 'Remind me when I leave items in my cart',
            'vault_photo_notifications': 'Notify me when my vault photo submissions are reviewed',
            'vault_featured_notifications': 'Notify me when my vault photos are featured',
        }
