from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import VaultPhoto
from products.models import Product


def vault_gallery(request):
    """
    Display the public Vault gallery with approved photos
    """
    from django.db.models import Exists, OuterRef

    photos = VaultPhoto.objects.filter(status='approved').select_related('user').prefetch_related('tagged_products')

    # Annotate photos with liked status for authenticated users
    if request.user.is_authenticated:
        photos = photos.annotate(
            is_liked=Exists(
                VaultPhoto.likes.through.objects.filter(
                    vaultphoto_id=OuterRef('pk'),
                    user_id=request.user.id
                )
            )
        )

    # Filter by product if specified
    product_filter = request.GET.get('product')
    if product_filter:
        photos = photos.filter(tagged_products__slug=product_filter)

    # Pagination
    paginator = Paginator(photos, 20)  # 20 photos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all products for filter dropdown
    all_products = Product.objects.filter(is_archived=False).order_by('name')

    context = {
        'photos': page_obj,
        'page_obj': page_obj,
        'product_filter': product_filter,
        'all_products': all_products,
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

        # Validate file size (5MB max)
        if image.size > 5 * 1024 * 1024:
            messages.error(request, 'File size must be less than 5MB.')
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
                messages.success(request, f'Photo by {photo.user.username} approved.')
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

        return redirect('vault:moderate_photos')

    # Filter options
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'all':
        photos = VaultPhoto.objects.all().select_related('user').prefetch_related('tagged_products')
    else:
        photos = VaultPhoto.objects.filter(status=status_filter).select_related('user').prefetch_related('tagged_products')

    context = {
        'photos': photos,
        'status_filter': status_filter,
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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': 'approved'})
    else:
        messages.success(request, f'Photo by {photo.user.username} has been approved.')
        return redirect('vault:moderate_photos')


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
        return redirect('vault:moderate_photos')


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