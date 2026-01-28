from django.db import models
from django.utils import timezone


class SeasonalTheme(models.Model):
    """
    Seasonal theme configuration for vault-hero animations.
    Supports multiple themes with priority-based activation.
    """
    THEME_TYPE_CHOICES = [
        ('new_years', 'New Years'),
        ('valentines', 'Valentines Day'),
        ('st_patricks', "Saint Patrick's Day"),
        ('mothers_day', "Mother's Day"),
        ('fathers_day', "Father's Day"),
        ('fourth_july', '4th of July'),
        ('rock_n_roll', "Rock'N'Roll Day"),
        ('thanksgiving', 'Thanksgiving'),
        ('christmas', 'Christmas'),
        ('everyday', 'Every Day (Gothic Metal)'),
        ('celebration', 'Celebration (Confetti)'),
    ]

    SPEED_CHOICES = [
        ('slow', 'Slow'),
        ('normal', 'Normal'),
        ('fast', 'Fast'),
    ]

    DENSITY_CHOICES = [
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('heavy', 'Heavy'),
    ]

    name = models.CharField(
        max_length=100,
        help_text="Display name for the theme (e.g., 'Christmas 2024')"
    )
    theme_type = models.CharField(
        max_length=20,
        choices=THEME_TYPE_CHOICES,
        unique=True,
        help_text="Type of seasonal theme - determines the animation style"
    )

    # Activation controls
    is_active = models.BooleanField(
        default=False,
        help_text="Enable/disable this theme"
    )
    is_paused = models.BooleanField(
        default=False,
        help_text="Temporarily pause animation without deactivating"
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority themes take precedence when multiple are active (0 = lowest)"
    )

    # Optional date constraints
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional: Theme activates after this date/time"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional: Theme deactivates after this date/time"
    )

    # Animation configuration
    animation_speed = models.CharField(
        max_length=20,
        choices=SPEED_CHOICES,
        default='normal',
        help_text="Animation playback speed"
    )
    particle_density = models.CharField(
        max_length=20,
        choices=DENSITY_CHOICES,
        default='medium',
        help_text="Density of animated particles"
    )

    # Custom CSS (for advanced users)
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS for this theme (advanced users only)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = "Seasonal Theme"
        verbose_name_plural = "Seasonal Themes"

    def __str__(self):
        status = "Active" if self.is_currently_active() else "Inactive"
        return f"{self.name} ({status})"

    def is_currently_active(self):
        """
        Check if theme is currently active considering all constraints:
        - is_active must be True
        - is_paused must be False
        - Current time must be within start_date and end_date (if set)
        """
        if not self.is_active:
            return False
        if self.is_paused:
            return False

        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False

        return True

    def get_status_display_text(self):
        """Return human-readable status"""
        if not self.is_active:
            return "Inactive"
        if self.is_paused:
            return "Paused"
        if not self.is_currently_active():
            now = timezone.now()
            if self.start_date and now < self.start_date:
                return "Scheduled"
            if self.end_date and now > self.end_date:
                return "Expired"
        return "Active"

    def get_theme_config(self):
        """
        Return theme configuration for JavaScript
        """
        return {
            'theme_type': self.theme_type,
            'speed': self.animation_speed,
            'density': self.particle_density,
            'is_paused': self.is_paused,
            'custom_css': self.custom_css,
        }
