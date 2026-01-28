from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SeasonalTheme
from .forms import SeasonalThemeForm


@staff_member_required
def admin_themes_list(request):
    """List all seasonal themes with filtering and search"""
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    sort = request.GET.get('sort', '-priority')

    themes = SeasonalTheme.objects.all()

    # Search by name
    if search:
        themes = themes.filter(Q(name__icontains=search))

    # Filter by status
    if status:
        if status == 'active':
            themes = themes.filter(is_active=True, is_paused=False)
        elif status == 'paused':
            themes = themes.filter(is_paused=True)
        elif status == 'inactive':
            themes = themes.filter(is_active=False)

    # Sorting
    valid_sorts = ['-priority', 'priority', '-created_at', 'created_at', 'name', '-name']
    if sort in valid_sorts:
        themes = themes.order_by(sort)

    # Pagination
    paginator = Paginator(themes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'sort': sort,
    }

    return render(request, 'themes/admin_themes_list.html', context)


@staff_member_required
def admin_themes_create(request):
    """Create a new seasonal theme"""
    if request.method == 'POST':
        form = SeasonalThemeForm(request.POST)
        if form.is_valid():
            theme = form.save()
            messages.success(request, f'Seasonal theme "{theme.name}" created successfully!')
            return redirect('admin_themes_list')
    else:
        form = SeasonalThemeForm()

    context = {
        'form': form,
        'title': 'Create Seasonal Theme',
        'submit_text': 'Create Theme',
        'is_edit': False,
    }

    return render(request, 'themes/admin_themes_form.html', context)


@staff_member_required
def admin_themes_edit(request, theme_id):
    """Edit an existing seasonal theme"""
    theme = get_object_or_404(SeasonalTheme, id=theme_id)

    if request.method == 'POST':
        form = SeasonalThemeForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, f'Seasonal theme "{theme.name}" updated successfully!')
            return redirect('admin_themes_list')
    else:
        form = SeasonalThemeForm(instance=theme)

    context = {
        'form': form,
        'theme': theme,
        'title': f'Edit Theme: {theme.name}',
        'submit_text': 'Update Theme',
        'is_edit': True,
    }

    return render(request, 'themes/admin_themes_form.html', context)


@staff_member_required
def admin_themes_toggle(request, theme_id):
    """Toggle theme active status (activate/deactivate)"""
    if request.method == 'POST':
        theme = get_object_or_404(SeasonalTheme, id=theme_id)
        theme.is_active = not theme.is_active
        theme.save()

        status = 'activated' if theme.is_active else 'deactivated'
        messages.success(request, f'Theme "{theme.name}" has been {status}!')

    return redirect('admin_themes_list')


@staff_member_required
def admin_themes_pause(request, theme_id):
    """Toggle theme pause status (play/pause animation)"""
    if request.method == 'POST':
        theme = get_object_or_404(SeasonalTheme, id=theme_id)
        theme.is_paused = not theme.is_paused
        theme.save()

        status = 'paused' if theme.is_paused else 'resumed'
        messages.success(request, f'Theme "{theme.name}" animation has been {status}!')

    return redirect('admin_themes_list')


@staff_member_required
def admin_themes_delete(request, theme_id):
    """Delete a seasonal theme"""
    if request.method == 'POST':
        theme = get_object_or_404(SeasonalTheme, id=theme_id)
        theme_name = theme.name
        theme.delete()
        messages.success(request, f'Theme "{theme_name}" has been deleted!')

    return redirect('admin_themes_list')


@staff_member_required
def admin_themes_preview(request, theme_id):
    """Preview a specific theme animation"""
    theme = get_object_or_404(SeasonalTheme, id=theme_id)

    context = {
        'theme': theme,
        'preview_mode': True,
    }

    return render(request, 'themes/admin_themes_preview.html', context)
