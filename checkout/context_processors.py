from .models import DiscountCode
from django.utils import timezone
import hashlib
import time
import json


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
        'offer_count': 0,
        'current_offer_index': 0,
        'expires_at': None,
        'expires_at_iso': None,
        'discount_value': 0,
        'is_high_value': False,  # For confetti effect on high-value discounts
    }

    if active_discounts.exists():
        banner_data['show_discount_banner'] = True
        banner_data['multiple_offers'] = active_discounts.count() > 1
        banner_data['offer_count'] = active_discounts.count()

        # Prepare data for all offers (for JavaScript cycling)
        for i, discount in enumerate(active_discounts):
            # Create clickable code span for copy functionality
            clickable_code = f'<span class="discount-code-text" data-code="{discount.code}" title="Click to copy">{discount.code}</span>'

            offer_data = {
                'code': discount.code,
                'message': discount.banner_message or f'{discount.discount_value}{"%" if discount.discount_type == "percentage" else "€"} OFF with code: {clickable_code}',
                'expires_at': discount.expires_at.isoformat() if discount.expires_at else None,
                'discount_value': float(discount.discount_value),
                'discount_type': discount.discount_type,
                'is_high_value': (discount.discount_value >= 20)
            }
            if discount.banner_message:
                # Replace {CODE} or {code} placeholders with clickable code
                offer_data['message'] = discount.banner_message.replace('{CODE}', clickable_code).replace('{code}', clickable_code)
            banner_data['all_offers'].append(offer_data)

        # If only one discount code, use it directly
        if active_discounts.count() == 1:
            selected_discount = active_discounts.first()
            banner_data['current_offer_index'] = 0
        else:
            # Multiple discount codes - implement rotation logic
            selected_discount = get_rotated_discount(active_discounts, request)
            # Find the index of the selected discount
            for i, d in enumerate(active_discounts):
                if d.code == selected_discount.code:
                    banner_data['current_offer_index'] = i
                    break

        banner_data['discount_code'] = selected_discount.code
        banner_data['discount_value'] = float(selected_discount.discount_value)

        # Determine if this is a high-value discount (20%+ or €20+)
        if selected_discount.discount_type == 'percentage':
            banner_data['is_high_value'] = selected_discount.discount_value >= 20
        else:
            banner_data['is_high_value'] = selected_discount.discount_value >= 20

        # Add expiration data for countdown
        if selected_discount.expires_at:
            banner_data['expires_at'] = selected_discount.expires_at
            banner_data['expires_at_iso'] = selected_discount.expires_at.isoformat()

        # Create clickable code span
        clickable_code = f'<span class="discount-code-text" data-code="{selected_discount.code}" title="Click to copy">{selected_discount.code}</span>'

        # Use custom banner message if provided, otherwise use default
        if selected_discount.banner_message:
            # Replace {CODE} or {code} placeholders with clickable code
            message = selected_discount.banner_message.replace('{CODE}', clickable_code).replace('{code}', clickable_code)
            banner_data['banner_message'] = message
        else:
            # Default message with the actual discount code
            if selected_discount.discount_type == 'percentage':
                discount_text = f"{selected_discount.discount_value}%"
            else:
                discount_text = f"€{selected_discount.discount_value}"

            banner_data['banner_message'] = f'{discount_text} OFF with code: {clickable_code}'

    # Serialize offers to JSON for safe embedding in JavaScript
    try:
        banner_data['all_offers_json'] = json.dumps(banner_data.get('all_offers', []))
    except Exception:
        banner_data['all_offers_json'] = '[]'

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