from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Order
from django.utils import timezone
from datetime import datetime
import csv
from django.http import HttpResponse

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
