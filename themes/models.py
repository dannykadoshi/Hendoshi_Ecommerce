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

    STRIP_COLOR_CHOICES = [
        ('theme', 'Match Theme Colors'),
        ('pink_yellow', 'Pink to Yellow (Default)'),
        ('custom', 'Custom Gradient'),
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

    # Message Strip Configuration
    show_message_strip = models.BooleanField(
        default=False,
        help_text="Display a scrolling message strip below the vault-hero"
    )
    strip_messages = models.TextField(
        blank=True,
        help_text="Messages separated by | (e.g., 'HAPPY VALENTINE'S | LOVE FULLY | SPREAD JOY')"
    )
    strip_color_scheme = models.CharField(
        max_length=20,
        choices=STRIP_COLOR_CHOICES,
        default='theme',
        help_text="Color scheme for the message strip"
    )
    strip_custom_gradient = models.CharField(
        max_length=200,
        blank=True,
        help_text="Custom CSS gradient (e.g., 'linear-gradient(135deg, #ff0000, #00ff00)')"
    )
    strip_scroll_speed = models.CharField(
        max_length=20,
        choices=SPEED_CHOICES,
        default='normal',
        help_text="Speed of the scrolling text animation"
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

    def get_strip_messages_list(self):
        """
        Parse strip_messages field and return as a list.
        Messages are separated by |
        """
        if not self.strip_messages:
            return []
        messages = [msg.strip() for msg in self.strip_messages.split('|') if msg.strip()]
        return messages

    def get_strip_gradient(self):
        """
        Return the CSS gradient for the message strip based on color scheme.
        """
        # Theme-specific color mappings
        theme_gradients = {
            'new_years': 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%)',
            'valentines': 'linear-gradient(135deg, #FF1493 0%, #FF69B4 50%, #FF1493 100%)',
            'st_patricks': 'linear-gradient(135deg, #228B22 0%, #32CD32 50%, #FFD700 100%)',
            'mothers_day': 'linear-gradient(135deg, #DDA0DD 0%, #FF69B4 50%, #DDA0DD 100%)',
            'fathers_day': 'linear-gradient(135deg, #4169E1 0%, #6495ED 50%, #4169E1 100%)',
            'fourth_july': 'linear-gradient(135deg, #DC143C 0%, #FFFFFF 50%, #4169E1 100%)',
            'rock_n_roll': 'linear-gradient(135deg, #8B008B 0%, #FF1493 50%, #000000 100%)',
            'thanksgiving': 'linear-gradient(135deg, #D2691E 0%, #FF8C00 50%, #8B4513 100%)',
            'christmas': 'linear-gradient(135deg, #DC143C 0%, #228B22 50%, #DC143C 100%)',
            'everyday': 'linear-gradient(135deg, #4B0082 0%, #8B0000 50%, #000000 100%)',
            'celebration': 'linear-gradient(135deg, #FF1493 0%, #FFD700 50%, #00CED1 100%)',
        }

        if self.strip_color_scheme == 'custom' and self.strip_custom_gradient:
            return self.strip_custom_gradient
        elif self.strip_color_scheme == 'theme':
            return theme_gradients.get(
                self.theme_type,
                'linear-gradient(135deg, var(--neon-pink) 0%, #ff6b9d 50%, var(--electric-yellow) 100%)'
            )
        else:  # pink_yellow default
            return 'linear-gradient(135deg, var(--neon-pink) 0%, #ff6b9d 50%, var(--electric-yellow) 100%)'

    def get_strip_scroll_duration(self):
        """
        Return CSS animation duration based on scroll speed.
        """
        speed_map = {
            'slow': '35s',
            'normal': '25s',
            'fast': '15s',
        }
        return speed_map.get(self.strip_scroll_speed, '25s')
