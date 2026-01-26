from .models import DiscountCode
from django.utils import timezone
import hashlib
import time


def discount_banner(request):
    """
    Context processor to make discount banner information available across all templates
    """
    # Get all active discount codes
    active_discounts = DiscountCode.objects.filter(
        is_active=True
    ).exclude(
        expires_at__lte=timezone.now()
    ).order_by('created_at')

    banner_data = {
        'show_discount_banner': False,
        'discount_code': None,
        'banner_message': '10% OFF your first order with code: <strong class="discount-code-text">WELCOME</strong>',
        'multiple_offers': False,
        'all_offers': [],
    }

    if active_discounts.exists():
        banner_data['show_discount_banner'] = True
        banner_data['multiple_offers'] = active_discounts.count() > 1

        # Prepare data for all offers (for JavaScript cycling)
        for discount in active_discounts:
            offer_data = {
                'code': discount.code,
                'message': discount.banner_message or f'{"%" if discount.discount_type == "percentage" else "€"}{discount.discount_value} OFF with code: <strong class="discount-code-text">{discount.code}</strong>'
            }
            if discount.banner_message:
                # Replace {CODE} or {code} placeholders with styled actual code
                styled_code = f'<strong class="discount-code-text">{discount.code}</strong>'
                offer_data['message'] = discount.banner_message.replace('{CODE}', styled_code).replace('{code}', styled_code)
            banner_data['all_offers'].append(offer_data)

        # If only one discount code, use it directly
        if active_discounts.count() == 1:
            selected_discount = active_discounts.first()
        else:
            # Multiple discount codes - implement rotation logic
            selected_discount = get_rotated_discount(active_discounts, request)

        banner_data['discount_code'] = selected_discount.code

        # Use custom banner message if provided, otherwise use default
        if selected_discount.banner_message:
            # Replace {CODE} or {code} placeholders with styled actual code
            styled_code = f'<strong class="discount-code-text">{selected_discount.code}</strong>'
            message = selected_discount.banner_message.replace('{CODE}', styled_code).replace('{code}', styled_code)
            banner_data['banner_message'] = message
        else:
            # Default message with the actual discount code
            if selected_discount.discount_type == 'percentage':
                discount_text = f"{selected_discount.discount_value}%"
            else:
                discount_text = f"€{selected_discount.discount_value}"

            banner_data['banner_message'] = f'{discount_text} OFF with code: <strong class="discount-code-text">{selected_discount.code}</strong>'

    return {
        'discount_banner': banner_data
    }


def get_rotated_discount(active_discounts, request):
    """
    Select a discount code for rotation based on time and session
    """
    # Get current time in hours (changes every hour)
    current_hour = int(time.time() // 3600)

    # Use session key or IP for user-specific rotation
    user_identifier = getattr(request, 'session', {}).get('session_key', '') or request.META.get('REMOTE_ADDR', 'anonymous')

    # Create a hash that combines time and user identifier for consistent but rotating selection
    rotation_seed = f"{current_hour}_{user_identifier}"
    rotation_hash = hashlib.md5(rotation_seed.encode()).hexdigest()

    # Convert hash to integer and use modulo to select discount
    discount_index = int(rotation_hash, 16) % len(active_discounts)

    return active_discounts[discount_index]