from django.utils import timezone
from .models import SeasonalTheme


def active_seasonal_theme(request):
    """
    Context processor to provide active seasonal theme to all templates.

    Priority logic:
    1. Get all active, non-paused themes
    2. Filter by current date (if constraints exist)
    3. Order by priority (descending)
    4. Return first match (highest priority wins)
    """
    now = timezone.now()

    # Get all potentially active themes ordered by priority
    themes = SeasonalTheme.objects.filter(
        is_active=True,
        is_paused=False
    ).order_by('-priority')

    active_theme = None

    for theme in themes:
        # Check date constraints
        if theme.start_date and now < theme.start_date:
            continue
        if theme.end_date and now > theme.end_date:
            continue

        # First valid theme by priority wins
        active_theme = theme
        break

    return {
        'seasonal_theme': active_theme,
        'has_seasonal_theme': active_theme is not None,
    }
