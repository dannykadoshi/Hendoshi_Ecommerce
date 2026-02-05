from django import forms
from .models import SeasonalTheme


class SeasonalThemeForm(forms.ModelForm):
    """Form for creating and editing seasonal themes"""

    class Meta:
        model = SeasonalTheme
        fields = [
            'name', 'theme_type', 'is_active', 'is_paused', 'priority',
            'start_date', 'end_date', 'animation_speed', 'particle_density',
            'custom_css',
            # Message Strip fields
            'show_message_strip', 'strip_messages', 'strip_color_scheme',
            'strip_custom_gradient', 'strip_scroll_speed'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Christmas 2024'
            }),
            'theme_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_paused': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1000',
                'placeholder': '0 = lowest priority'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'animation_speed': forms.Select(attrs={
                'class': 'form-select'
            }),
            'particle_density': forms.Select(attrs={
                'class': 'form-select'
            }),
            'custom_css': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '/* Custom CSS for advanced users */'
            }),
            # Message Strip widgets
            'show_message_strip': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'strip_messages': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "HAPPY VALENTINE'S DAY | LOVE FULLY | SPREAD THE LOVE"
            }),
            'strip_color_scheme': forms.Select(attrs={
                'class': 'form-select'
            }),
            'strip_custom_gradient': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'linear-gradient(135deg, #ff0000, #00ff00)'
            }),
            'strip_scroll_speed': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Theme Name',
            'theme_type': 'Theme Type',
            'is_active': 'Active',
            'is_paused': 'Paused',
            'priority': 'Priority',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'animation_speed': 'Animation Speed',
            'particle_density': 'Particle Density',
            'custom_css': 'Custom CSS',
            # Message Strip labels
            'show_message_strip': 'Show Message Strip',
            'strip_messages': 'Strip Messages',
            'strip_color_scheme': 'Color Scheme',
            'strip_custom_gradient': 'Custom Gradient',
            'strip_scroll_speed': 'Scroll Speed',
        }
        help_texts = {
            'priority': 'Higher number = higher priority. When multiple themes are active, the highest priority wins.',
            'start_date': 'Leave blank to start immediately when activated.',
            'end_date': 'Leave blank for no end date.',
            'custom_css': 'Add custom CSS to override or extend the default theme styles.',
            # Message Strip help texts
            'show_message_strip': 'Display a scrolling message strip below the page-hero section.',
            'strip_messages': 'Enter messages separated by | (pipe). Each message will be separated by a skull icon.',
            'strip_color_scheme': 'Choose auto-matching theme colors, the default pink-yellow, or set a custom gradient.',
            'strip_custom_gradient': 'Only used when Color Scheme is "Custom Gradient".',
            'strip_scroll_speed': 'How fast the text scrolls horizontally.',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data

    def clean_theme_type(self):
        """Ensure theme_type is unique (excluding current instance on edit)"""
        theme_type = self.cleaned_data.get('theme_type')
        if theme_type:
            existing = SeasonalTheme.objects.filter(theme_type=theme_type)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    f"A theme with type '{dict(SeasonalTheme.THEME_TYPE_CHOICES).get(theme_type)}' already exists."
                )
        return theme_type
