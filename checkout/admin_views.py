from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, DiscountCode
from django.utils import timezone
from datetime import datetime
import csv
from django.http import HttpResponse
from django.contrib import messages
from .forms import DiscountCodeForm
from .forms import ShippingRateForm
from .models import ShippingRate

@staff_member_required
def admin_orders_list(request):
    # Filtering
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    orders = Order.objects.all()

    if status:
        orders = orders.filter(status=status)
    if search:
        orders = orders.filter(Q(order_number__icontains=search) | Q(email__icontains=search) | Q(user__email__icontains=search))
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            orders = orders.filter(created_at__gte=start)
        except Exception:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = timezone.make_aware(datetime.combine(end, datetime.max.time()))
            orders = orders.filter(created_at__lte=end)
        except Exception:
            pass
    if sort:
        orders = orders.order_by(sort)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # CSV export
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Customer', 'Email', 'Date', 'Total', 'Status'])
        for order in orders:
            writer.writerow([
                order.order_number,
                order.user.get_full_name() if order.user else '',
                order.email,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.total_amount,
                order.status
            ])
        return response

    return render(request, 'checkout/admin_orders_list.html', {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'sort': sort,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required
def admin_discount_codes_list(request):
    # Filtering
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    sort = request.GET.get('sort', '-created_at')
    
    discount_codes = DiscountCode.objects.all()

    if search:
        discount_codes = discount_codes.filter(Q(code__icontains=search))
    if is_active:
        if is_active == 'active':
            discount_codes = discount_codes.filter(is_active=True)
        elif is_active == 'inactive':
            discount_codes = discount_codes.filter(is_active=False)
    
    if sort:
        discount_codes = discount_codes.order_by(sort)

    paginator = Paginator(discount_codes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'checkout/admin_discount_codes_list.html', {
        'page_obj': page_obj,
        'search': search,
        'is_active': is_active,
        'sort': sort,
    })


@staff_member_required
def admin_discount_codes_create(request):
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount code created successfully!')
            return redirect('admin_discount_codes_list')
    else:
        form = DiscountCodeForm()
    
    return render(request, 'checkout/admin_discount_codes_form.html', {
        'form': form,
        'title': 'Create Discount Code',
        'submit_text': 'Create Code'
    })


@staff_member_required
def admin_discount_codes_edit(request, code_id):
    code = get_object_or_404(DiscountCode, id=code_id)
    
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST, instance=code)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount code updated successfully!')
            return redirect('admin_discount_codes_list')
    else:
        form = DiscountCodeForm(instance=code)
    
    return render(request, 'checkout/admin_discount_codes_form.html', {
        'form': form,
        'title': 'Edit Discount Code',
        'submit_text': 'Update Code'
    })


@staff_member_required
def admin_discount_codes_toggle(request, code_id):
    if request.method == 'POST':
        code = get_object_or_404(DiscountCode, id=code_id)
        code.is_active = not code.is_active
        code.save()
        
        status = 'activated' if code.is_active else 'paused'
        messages.success(request, f'Discount code {code.code} has been {status}!')
    
    return redirect('admin_discount_codes_list')


@staff_member_required
def admin_discount_codes_delete(request, code_id):
    if request.method == 'POST':
        code = get_object_or_404(DiscountCode, id=code_id)
        code_name = code.code
        code.delete()
        messages.success(request, f'Discount code {code_name} has been deleted!')
    
    return redirect('admin_discount_codes_list')


@staff_member_required
def admin_shipping_list(request):
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')

    shipping_qs = ShippingRate.objects.all()
    if search:
        shipping_qs = shipping_qs.filter(name__icontains=search)
    if sort:
        shipping_qs = shipping_qs.order_by(sort)

    paginator = Paginator(shipping_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'checkout/admin_shipping_list.html', {
        'page_obj': page_obj,
        'search': search,
        'sort': sort,
    })


@staff_member_required
def admin_shipping_create(request):
    if request.method == 'POST':
        form = ShippingRateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping rate created successfully!')
            return redirect('admin_shipping_list')
    else:
        form = ShippingRateForm()

    return render(request, 'checkout/admin_shipping_form.html', {
        'form': form,
        'title': 'Create Shipping Rate',
        'submit_text': 'Create'
    })


@staff_member_required
def admin_shipping_edit(request, ship_id):
    rate = get_object_or_404(ShippingRate, id=ship_id)
    if request.method == 'POST':
        form = ShippingRateForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping rate updated successfully!')
            return redirect('admin_shipping_list')
    else:
        form = ShippingRateForm(instance=rate)

    return render(request, 'checkout/admin_shipping_form.html', {
        'form': form,
        'title': 'Edit Shipping Rate',
        'submit_text': 'Update'
    })


@staff_member_required
def admin_shipping_toggle_active(request, ship_id):
    if request.method == 'POST':
        rate = get_object_or_404(ShippingRate, id=ship_id)
        rate.is_active = not rate.is_active
        rate.save()
        status = 'activated' if rate.is_active else 'paused'
        messages.success(request, f'Shipping rate "{rate.name}" has been {status}.')
    return redirect('admin_shipping_list')


@staff_member_required
def admin_shipping_set_standard(request, ship_id):
    if request.method == 'POST':
        rate = get_object_or_404(ShippingRate, id=ship_id)
        # mark this as standard; model.save will unset others
        rate.is_standard = True
        rate.save()
        messages.success(request, f'Shipping rate "{rate.name}" set as standard.')
    return redirect('admin_shipping_list')


@staff_member_required
def admin_shipping_delete(request, ship_id):
    if request.method == 'POST':
        rate = get_object_or_404(ShippingRate, id=ship_id)
        name = rate.name
        rate.delete()
        messages.success(request, f'Shipping rate "{name}" deleted.')
    return redirect('admin_shipping_list')
