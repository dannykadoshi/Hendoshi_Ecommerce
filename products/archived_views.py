from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product


def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_admin)
def archived_products(request):
    """
    Staff-only view to list all archived (soft-deleted) products
    """
    archived = Product.objects.filter(is_archived=True)
    context = {
        'archived_products': archived,
    }
    return render(request, 'products/archived_products.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def restore_product(request, slug):
    """
    Staff-only view to restore an archived product
    """
    product = get_object_or_404(Product, slug=slug, is_archived=True)
    if request.method == 'POST':
        product.is_archived = False
        product.save()
        messages.success(request, f'Product "{product.name}" has been restored!')
        return redirect('archived_products')
    context = {
        'product': product,
    }
    return render(request, 'products/confirm_restore.html', context)
