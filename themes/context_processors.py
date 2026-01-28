from django.utils import timezone


def active_seasonal_theme(request):
    """
    Context processor to provide active seasonal theme to all templates.

    Priority logic:
    1. Get all active, non-paused themes
    2. Filter by current date (if constraints exist)
    3. Order by priority (descending)
    4. Return first match (highest priority wins)
    """
    # Default context if anything fails
    default_context = {
        'seasonal_theme': None,
        'has_seasonal_theme': False,
        'show_theme_message_strip': False,
    }

    try:
        # Import here to prevent import errors if model doesn't exist
        from .models import SeasonalTheme

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

        # Build context data
        context = {
            'seasonal_theme': active_theme,
            'has_seasonal_theme': active_theme is not None,
        }

        # Add message strip data if theme has strip enabled
        if active_theme and active_theme.show_message_strip:
            messages = active_theme.get_strip_messages_list()
            if messages:
                # Duplicate messages for seamless loop (like philosophy strip)
                context['theme_strip_messages'] = messages + messages
                context['theme_strip_gradient'] = active_theme.get_strip_gradient()
                context['theme_strip_speed'] = active_theme.strip_scroll_speed
                context['show_theme_message_strip'] = True
            else:
                context['show_theme_message_strip'] = False
        else:
            context['show_theme_message_strip'] = False

        return context

    except Exception:
        # If anything fails (missing table, import error, etc.), return defaults
        return default_context
