from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
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
            products = Product.objects.filter(id__in=product_ids)
            photo.tagged_products.set(products)

        messages.success(request, 'Your photo has been submitted for approval. You will be notified once it\'s reviewed.')
        return redirect('vault:vault_gallery')

    # GET request - show form
    products = Product.objects.filter(is_archived=False).select_related('collection').order_by('collection__name', 'name')
    collections = {}
    for product in products:
        collection_name = product.collection.name if product.collection else 'Other'
        if collection_name not in collections:
            collections[collection_name] = []
        collections[collection_name].append(product)
    
    context = {
        'collections': collections,
    }
    return render(request, 'vault/submit_photo.html', context)


def photo_detail(request, photo_id):
    """
    Display detailed view of a single photo
    """
    photo = get_object_or_404(VaultPhoto, id=photo_id, status='approved')
    liked = photo.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    context = {
        'photo': photo,
        'liked': liked,
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
            photo_ids = [int(pid) for pid in request.POST.getlist('selected_photos') if pid]
            photos = VaultPhoto.objects.filter(id__in=photo_ids)
            if bulk_action == 'approve':
                photos.update(status='approved')
                messages.success(request, f'Approved {photos.count()} photos.')
            elif bulk_action == 'reject':
                photos.update(status='rejected')
                messages.success(request, f'Rejected {photos.count()} photos.')
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
                messages.success(request, f'Photo by {photo.user.username} rejected.')

        return redirect('vault:moderate_photos')

    photos = VaultPhoto.objects.filter(status='pending').select_related('user').prefetch_related('tagged_products')

    # Filter options
    status_filter = request.GET.get('status', 'pending')
    if status_filter != 'all':
        photos = photos.filter(status=status_filter)

    username_filter = request.GET.get('username')
    if username_filter:
        photos = photos.filter(user__username__icontains=username_filter)

    context = {
        'photos': photos,
        'status_filter': status_filter,
        'username_filter': username_filter,
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