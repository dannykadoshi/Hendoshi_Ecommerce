from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CollectionForm, ProductTypeForm
from .models import Collection, ProductType


def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_admin)
def list_collections(request):
    collections = Collection.objects.all().order_by('name')
    return render(request, 'products/admin_collections_list.html', {'collections': collections})


@login_required
@user_passes_test(is_staff_or_admin)
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection created successfully')
            return redirect('admin_list_collections')
    else:
        form = CollectionForm()
    return render(request, 'products/admin_create_collection.html', {'form': form})


@login_required
@user_passes_test(is_staff_or_admin)
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated')
            return redirect('admin_list_collections')
    else:
        form = CollectionForm(instance=collection)
    return render(request, 'products/admin_create_collection.html', {'form': form, 'collection': collection})


@login_required
@user_passes_test(is_staff_or_admin)
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted')
        return redirect('admin_list_collections')
    return render(request, 'products/admin_confirm_delete_collection.html', {'collection': collection})


@login_required
@user_passes_test(is_staff_or_admin)
def list_product_types(request):
    types = ProductType.objects.all().order_by('name')
    return render(request, 'products/admin_product_types_list.html', {'types': types})


@login_required
@user_passes_test(is_staff_or_admin)
def create_product_type(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product type created')
            return redirect('admin_list_product_types')
    else:
        form = ProductTypeForm()
    return render(request, 'products/admin_create_product_type.html', {'form': form})


@login_required
@user_passes_test(is_staff_or_admin)
def edit_product_type(request, pk):
    pt = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, instance=pt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product type updated')
            return redirect('admin_list_product_types')
    else:
        form = ProductTypeForm(instance=pt)
    return render(request, 'products/admin_create_product_type.html', {'form': form, 'product_type': pt})


@login_required
@user_passes_test(is_staff_or_admin)
def delete_product_type(request, pk):
    pt = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        pt.delete()
        messages.success(request, 'Product type deleted')
        return redirect('admin_list_product_types')
    return render(request, 'products/admin_confirm_delete_product_type.html', {'product_type': pt})
