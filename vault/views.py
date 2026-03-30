from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.cache import cache_control
from .models import VaultPhoto
from products.models import Product


def _auto_feature_photos(num_photos=6, weeks=1):
    """
    Run the weekly featuring cycle automatically — no cron job needed.
    Called from vault_gallery whenever active featured photos have expired.
    """
    from datetime import timedelta

    # Expire any photos whose feature window has passed
    VaultPhoto.objects.filter(
        is_featured=True,
        featured_until__lt=timezone.now()
    ).update(is_featured=False, featured_until=None)

    # Score recent photos (last 30 days first, fall back to all approved)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    candidates = VaultPhoto.objects.filter(status='approved', created_at__gte=thirty_days_ago)
    if not candidates.exists():
        candidates = VaultPhoto.objects.filter(status='approved')

    for photo in candidates:
        like_score = photo.likes.count() * 10
        vote_score = photo.vote_score * 15
        days_old = (timezone.now() - photo.created_at).days
        age_boost = max(0, (30 - days_old) / 30 * 20)
        score = max(0, like_score + vote_score + int(age_boost))
        VaultPhoto.objects.filter(pk=photo.pk).update(feature_score=score)

    top_photos = list(candidates.order_by('-feature_score')[:num_photos])
    featured_until = timezone.now() + timedelta(weeks=weeks)
    top_ids = [p.pk for p in top_photos]
    now = timezone.now()

    VaultPhoto.objects.filter(pk__in=top_ids).update(
        is_featured=True,
        featured_until=featured_until
    )
    # Only stamp featured_date the first time a photo is featured
    VaultPhoto.objects.filter(pk__in=top_ids, featured_date__isnull=True).update(
        featured_date=now
    )


@cache_control(max_age=3600, public=True)
def vault_gallery(request):
    """
    Display the public Vault gallery with approved photos.
    Cache-Control: private, max-age=60 — browser caches for 60s;
    private prevents shared CDN caches from storing per-user like/vote state.
    """
    from django.db.models import Exists, OuterRef, Count, Case, When, BooleanField

    # Auto-feature: ensure at least 2 featured photos are active at all times
    active_featured_count = VaultPhoto.objects.filter(is_featured=True, featured_until__gt=timezone.now()).count()
    if active_featured_count < 2 and VaultPhoto.objects.filter(status='approved').exists():
        _auto_feature_photos()

    # Base queryset with optimized queries
    photos = VaultPhoto.objects.filter(status='approved').select_related('user').prefetch_related('tagged_products')

    # Use more efficient annotation for user-specific data
    if request.user.is_authenticated:
        # Single query to get user's interactions with all photos
        user_likes = VaultPhoto.likes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )
        user_upvotes = VaultPhoto.upvotes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )
        user_downvotes = VaultPhoto.downvotes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )

        photos = photos.annotate(
            is_liked=Exists(user_likes),
            user_upvoted=Exists(user_upvotes),
            user_downvoted=Exists(user_downvotes)
        )

    # Filter functionality removed - keeping all photos

    # Get featured photos with optimized queries
    featured_photos = VaultPhoto.objects.filter(
        status='approved',
        is_featured=True,
        featured_until__gt=timezone.now()
    ).select_related('user').prefetch_related('tagged_products').annotate(
        like_count=Count('likes')
    ).order_by('-feature_score')[:10]

    # Fallback to top photos if no featured ones
    if not featured_photos.exists():
        featured_photos = VaultPhoto.objects.filter(
            status='approved'
        ).annotate(
            like_count=Count('likes')
        ).select_related('user').prefetch_related('tagged_products').order_by('-like_count', '-created_at')[:10]

    # Annotate featured photos efficiently
    if request.user.is_authenticated:
        featured_likes = VaultPhoto.likes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )
        featured_upvotes = VaultPhoto.upvotes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )
        featured_downvotes = VaultPhoto.downvotes.through.objects.filter(
            user_id=request.user.id,
            vaultphoto_id=OuterRef('pk')
        )

        featured_photos = featured_photos.annotate(
            is_liked=Exists(featured_likes),
            user_upvoted=Exists(featured_upvotes),
            user_downvoted=Exists(featured_downvotes)
        )

    # Pagination with optimized page size
    paginator = Paginator(photos, 12)  # Reduced from 20 to 12 for better performance
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get products efficiently
    all_products = Product.objects.filter(is_archived=False).order_by('name')

    # Get products with counts more efficiently
    products_with_counts = Product.objects.filter(
        is_archived=False,
        vault_photos__status='approved'
    ).annotate(
        photo_count=Count('vault_photos', distinct=True)
    ).order_by('-photo_count')[:8]

    context = {
        'photos': page_obj,
        'page_obj': page_obj,
        'all_products': all_products,
        'products_with_counts': products_with_counts,
        'featured_photos': featured_photos,
    }
    return render(request, 'vault/vault_gallery.html', context)


@login_required
def submit_photo(request):
    """
    Handle photo submission form
    """
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        product_ids = request.POST.getlist('products')

        if not image:
            messages.error(request, 'Please upload an image.')
            return redirect('vault:submit_photo')

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image.content_type not in allowed_types:
            messages.error(request, 'Only JPG and PNG files are allowed.')
            return redirect('vault:submit_photo')

        # Validate file size (15MB max)
        if image.size > 15 * 1024 * 1024:
            messages.error(request, 'File size must be less than 15MB.')
            return redirect('vault:submit_photo')

        # Create photo
        photo = VaultPhoto.objects.create(
            user=request.user,
            image=image,
            caption=caption[:800] if caption else ''
        )

        # Add tagged products
        if product_ids:
            # Filter out empty strings and convert to integers
            valid_product_ids = [int(pid) for pid in product_ids if pid and pid.strip()]
            if valid_product_ids:
                products = Product.objects.filter(id__in=valid_product_ids)
                photo.tagged_products.set(products)

        messages.success(request, 'Your photo has been submitted for approval. You will be notified once it\'s reviewed.')
        return redirect('vault:vault_gallery')

    # GET request - show form
    products = Product.objects.filter(is_archived=False).order_by('name')
    
    context = {
        'all_products': products,
    }
    return render(request, 'vault/submit_photo.html', context)


def photo_detail(request, photo_id):
    """
    Display detailed view of a single photo
    """
    photo = get_object_or_404(VaultPhoto, id=photo_id, status='approved')
    liked = photo.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    user_upvoted = photo.upvotes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    user_downvoted = photo.downvotes.filter(id=request.user.id).exists() if request.user.is_authenticated else False

    # Get all approved photos ordered by creation date (newest first) - exclude archived
    all_photos = list(VaultPhoto.objects.filter(status='approved').order_by('-created_at'))

    # Find current photo's position
    current_index = None
    for i, p in enumerate(all_photos):
        if p.id == photo.id:
            current_index = i
            break

    # Get previous and next photos
    prev_photo = None
    next_photo = None
    if current_index is not None:
        if current_index > 0:
            prev_photo = all_photos[current_index - 1]
        if current_index < len(all_photos) - 1:
            next_photo = all_photos[current_index + 1]

    context = {
        'photo': photo,
        'liked': liked,
        'user_upvoted': user_upvoted,
        'user_downvoted': user_downvoted,
        'prev_photo': prev_photo,
        'next_photo': next_photo,
    }
    return render(request, 'vault/photo_detail.html', context)


@login_required
def moderate_photos(request):
    """
    Admin moderation queue - only for staff
    """
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('vault:vault_gallery')

    if request.method == 'POST':
        photo_id = request.POST.get('photo_id')
        action = request.POST.get('action')
        bulk_action = request.POST.get('bulk_action')

        if bulk_action:
            # Handle bulk actions
            selected_photos_str = request.POST.get('selected_photos', '')
            photo_ids = [int(pid.strip()) for pid in selected_photos_str.split(',') if pid.strip()]
            photos = VaultPhoto.objects.filter(id__in=photo_ids)
            if bulk_action == 'approve':
                photos.update(status='approved')
                messages.success(request, f'Approved {photos.count()} photos.')
            elif bulk_action == 'reject':
                photos.update(status='rejected')
                messages.success(request, f'Rejected {photos.count()} photos.')
            elif bulk_action == 'archive':
                photos.update(status='archived')
                messages.success(request, f'Archived {photos.count()} photos.')
            elif bulk_action == 'delete':
                count = photos.count()
                photos.delete()
                messages.success(request, f'Permanently deleted {count} photos.')
        elif photo_id and action:
            # Handle single actions
            photo = get_object_or_404(VaultPhoto, id=photo_id)
            if action == 'approve':
                photo.status = 'approved'
                photo.save()

                # Send approval email to the user
                try:
                    # Check if user has vault photo notifications enabled
                    from notifications.models import NotificationPreference
                    prefs = NotificationPreference.objects.get_or_create(user=photo.user)[0]
                    if prefs.email_notifications_enabled and prefs.vault_photo_notifications:
                        # Send approval email
                        subject = '🎉 Your HENDOSHI Vault Photo is Approved!'
                        context = {
                            'user': photo.user,
                            'profile': photo.user.userprofile,
                            'photo': photo,
                            'site_url': settings.SITE_URL,
                        }
                        html_message = render_to_string('notifications/emails/photo_approved.html', context)
                        plain_message = f"""
                        Hi {photo.user.username},

                        Congratulations! 🎉 Your photo has been approved and is now live in The HENDOSHI Vault!

                        "{photo.caption or 'Untitled'}"

                        View your approved photo: {settings.SITE_URL}/vault/photo/{photo.id}/

                        Keep sharing your HENDOSHI style! 🖤

                        Best regards,
                        The HENDOSHI Team
                        """

                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[photo.user.email],
                            html_message=html_message,
                            fail_silently=True
                        )
                        messages.success(request, f'Photo by {photo.user.username} approved and notification email sent.')
                    else:
                        messages.success(request, f'Photo by {photo.user.username} approved. (User has notifications disabled)')
                except Exception as e:
                    messages.warning(request, f'Photo approved but email notification failed: {str(e)}')
            elif action == 'reject':
                photo.status = 'rejected'
                photo.save()

                # Send rejection email with reason if provided
                rejection_reason = request.POST.get('rejection_reason', '').strip()
                if rejection_reason:
                    try:
                        # Check if user has vault photo notifications enabled
                        from notifications.models import NotificationPreference
                        prefs = NotificationPreference.objects.get_or_create(user=photo.user)[0]
                        if prefs.email_notifications_enabled and prefs.vault_photo_notifications:
                            # Send email to user
                            subject = f'Your HENDOSHI Vault photo has been reviewed'
                            context = {
                                'user': photo.user,
                                'profile': photo.user.userprofile,
                                'photo': photo,
                                'rejection_reason': rejection_reason,
                                'site_url': settings.SITE_URL,
                            }
                            html_message = render_to_string('notifications/emails/photo_rejected.html', context)
                            plain_message = f"""
                            Hi {photo.user.username},

                            Your photo submission to The HENDOSHI Vault has been reviewed.

                            Unfortunately, your photo was not approved for the following reason:

                            {rejection_reason}

                            You can submit a new photo anytime at: {settings.SITE_URL}/vault/submit/

                            Best regards,
                            The HENDOSHI Team
                            """

                            send_mail(
                                subject=subject,
                                message=plain_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[photo.user.email],
                                html_message=html_message,
                                fail_silently=True
                            )
                            messages.success(request, f'Photo by {photo.user.username} rejected and notification email sent.')
                        else:
                            messages.success(request, f'Photo by {photo.user.username} rejected. (User has notifications disabled)')
                    except Exception as e:
                        messages.warning(request, f'Photo rejected but email notification failed: {str(e)}')
                else:
                    messages.success(request, f'Photo by {photo.user.username} rejected.')
            elif action == 'archive':
                photo.status = 'archived'
                photo.save()
                messages.success(request, f'Photo by {photo.user.username} archived.')
            elif action == 'delete':
                photo.delete()
                messages.success(request, f'Photo by {photo.user.username} permanently deleted.')

        # Redirect back to the referring page (preserve filters/search),
        # falling back to the moderate_photos view if referrer is not set.
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect(reverse('vault:moderate_photos'))

    # Filter options
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()

    if status_filter == 'all':
        photos = VaultPhoto.objects.all().select_related('user').prefetch_related('tagged_products')
    else:
        photos = VaultPhoto.objects.filter(status=status_filter).select_related('user').prefetch_related('tagged_products')

    # Apply search filter if provided
    if search_query:
        photos = photos.filter(user__username__icontains=search_query)

    context = {
        'photos': photos,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'vault/moderate_photos.html', context)


@login_required
def approve_photo(request, photo_id):
    """
    Approve a photo via AJAX or redirect
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    photo = get_object_or_404(VaultPhoto, id=photo_id)
    photo.status = 'approved'
    photo.save()

    # Send approval email to the user
    try:
        # Check if user has vault photo notifications enabled
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=photo.user)[0]
        if prefs.email_notifications_enabled and prefs.vault_photo_notifications:
            # Send approval email
            subject = '🎉 Your HENDOSHI Vault Photo is Approved!'
            context = {
                'user': photo.user,
                'profile': photo.user.userprofile,
                'photo': photo,
                'site_url': settings.SITE_URL,
            }
            html_message = render_to_string('notifications/emails/photo_approved.html', context)
            plain_message = f"""
            Hi {photo.user.username},

            Congratulations! 🎉 Your photo has been approved and is now live in The HENDOSHI Vault!

            "{photo.caption or 'Untitled'}"

            View your approved photo: {settings.SITE_URL}/vault/photo/{photo.id}/

            Keep sharing your HENDOSHI style! 🖤

            Best regards,
            The HENDOSHI Team
            """

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[photo.user.email],
                html_message=html_message,
                fail_silently=True
            )
    except Exception as e:
        # Email sending failed, but photo is still approved
        pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'approved'})
    else:
        messages.success(request, f'Photo by {photo.user.username} has been approved.')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect(reverse('vault:moderate_photos'))


@login_required
def reject_photo(request, photo_id):
    """
    Reject a photo via AJAX or redirect
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    photo = get_object_or_404(VaultPhoto, id=photo_id)
    photo.status = 'rejected'
    photo.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'rejected'})
    else:
        messages.success(request, f'Photo by {photo.user.username} has been rejected.')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect(reverse('vault:moderate_photos'))


@login_required
def like_photo(request, photo_id):
    """
    Handle liking/unliking a photo via AJAX
    """
    if request.method == 'POST':
        photo = get_object_or_404(VaultPhoto, id=photo_id)
        if request.user in photo.likes.all():
            photo.likes.remove(request.user)
            liked = False
        else:
            photo.likes.add(request.user)
            liked = True
        return JsonResponse({'likes': photo.likes.count(), 'liked': liked})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def hall_of_fame(request):
    """
    Display the Hall of Fame - past featured photos
    """
    from django.db.models import Exists, OuterRef, Q

    # Show photos that are currently featured OR have ever been featured
    hall_photos = VaultPhoto.objects.filter(
        Q(featured_date__isnull=False) | Q(is_featured=True),
        status='approved',
    ).select_related('user').prefetch_related('tagged_products').order_by('-featured_date', '-feature_score')

    # Fallback: never leave Hall of Fame empty — show top approved photos by score
    if not hall_photos.exists():
        hall_photos = VaultPhoto.objects.filter(
            status='approved'
        ).select_related('user').prefetch_related('tagged_products').order_by('-feature_score', '-created_at')

    # Annotate photos with liked status for authenticated users
    if request.user.is_authenticated:
        hall_photos = hall_photos.annotate(
            is_liked=Exists(
                VaultPhoto.likes.through.objects.filter(
                    vaultphoto_id=OuterRef('pk'),
                    user_id=request.user.id
                )
            ),
            user_upvoted=Exists(
                VaultPhoto.upvotes.through.objects.filter(
                    vaultphoto_id=OuterRef('pk'),
                    user_id=request.user.id
                )
            ),
            user_downvoted=Exists(
                VaultPhoto.downvotes.through.objects.filter(
                    vaultphoto_id=OuterRef('pk'),
                    user_id=request.user.id
                )
            )
        )

    # Pagination - 20 photos per page
    paginator = Paginator(hall_photos, 20)
    page = request.GET.get('page')
    try:
        hall_photos_page = paginator.page(page)
    except Exception:
        hall_photos_page = paginator.page(1)

    context = {
        'hall_photos': hall_photos_page,
        'total_featured': hall_photos.count(),
    }
    return render(request, 'vault/hall_of_fame.html', context)


def hall_of_fame_overview(request):
    """
    Display the Hall of Fame overview page with description and qualification criteria
    """
    # Get total count of featured photos for the description
    total_featured = VaultPhoto.objects.filter(
        status='approved',
        featured_date__isnull=False
    ).count()

    context = {
        'total_featured': total_featured,
    }
    return render(request, 'vault/hall_of_fame_overview.html', context)


@login_required
def vote_photo(request, photo_id, vote_type):
    """
    Handle upvoting/downvoting of photos
    vote_type should be 'up' or 'down'
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    photo = get_object_or_404(VaultPhoto, id=photo_id, status='approved')

    # Prevent users from voting on their own photos
    if photo.user == request.user:
        return JsonResponse({'error': 'Cannot vote on your own photos'}, status=400)

    # Check current vote status
    has_upvote = photo.upvotes.filter(id=request.user.id).exists()
    has_downvote = photo.downvotes.filter(id=request.user.id).exists()

    # Determine the action based on current state and requested vote
    if vote_type == 'up':
        if has_upvote:
            # Clicking upvote when already upvoted - remove the upvote (toggle off)
            photo.upvotes.remove(request.user)
            user_vote = None
        else:
            # Remove any existing downvote and add upvote
            photo.downvotes.remove(request.user)
            photo.upvotes.add(request.user)
            user_vote = 'up'
    elif vote_type == 'down':
        if has_downvote:
            # Clicking downvote when already downvoted - remove the downvote (toggle off)
            photo.downvotes.remove(request.user)
            user_vote = None
        else:
            # Remove any existing upvote and add downvote
            photo.upvotes.remove(request.user)
            photo.downvotes.add(request.user)
            user_vote = 'down'
    else:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    # Update the vote score
    photo.vote_score = photo.upvotes.count() - photo.downvotes.count()
    photo.save()

    return JsonResponse({
        'upvotes': photo.upvotes.count(),
        'downvotes': photo.downvotes.count(),
        'vote_score': photo.vote_score,
        'user_vote': user_vote
    })