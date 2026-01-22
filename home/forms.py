from django import forms


class ContactForm(forms.Form):
    """Contact form for customer support inquiries."""

    SUBJECT_CHOICES = [
        ('', 'Select a subject...'),
        ('order_issue', 'Order Issue'),
        ('product_question', 'Product Question'),
        ('general_inquiry', 'General Inquiry'),
    ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
            'autocomplete': 'name',
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )

    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
        })
    )

    order_number = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., HEN-ABC12345 (optional)',
        })
    )

    message = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'How can we help you?',
            'rows': 6,
            'maxlength': '1000',
        })
    )

    def clean_message(self):
        """Ensure message doesn't exceed 1000 characters."""
        message = self.cleaned_data.get('message', '')
        if len(message) > 1000:
            raise forms.ValidationError('Message must be 1000 characters or less.')
        return message
