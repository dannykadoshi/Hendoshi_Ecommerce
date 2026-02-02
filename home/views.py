from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from products.models import Collection
from .forms import ContactForm


def index(request):
    """
    View to return the homepage
    """
    # Get all collections with products, ordered by product count (most popular first)
    collections_data = []

    # Get all collections and calculate their product counts
    all_collections = Collection.objects.all()
    for collection in all_collections:
        products = collection.products.filter(is_active=True, is_archived=False)
        product_count = products.count()
        if product_count > 0:  # Only show collections that have products
            # Get most popular product (featured first, then most recently created)
            hero_product = (products.filter(featured=True).first() or 
                          products.order_by('-created_at').first())
            
            collections_data.append({
                'name': collection.name,
                'slug': collection.slug,
                'product_count': product_count,
                'hero_product': hero_product,
            })

    # Sort by product count (highest first), then by name
    collections_data.sort(key=lambda x: (-x['product_count'], x['name']))

    context = {
        'collections': collections_data
    }

    return render(request, 'home/index.html', context)


def contact(request):
    """
    View to handle contact form submissions.
    Sends notification email to admin and confirmation email to customer.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject_key = form.cleaned_data['subject']
            order_number = form.cleaned_data['order_number']
            message_body = form.cleaned_data['message']

            # Map subject key to readable text
            subject_map = {
                'order_issue': 'Order Issue',
                'product_question': 'Product Question',
                'general_inquiry': 'General Inquiry',
            }
            subject_text = subject_map.get(subject_key, 'General Inquiry')

            # Prepare context for email templates
            email_context = {
                'name': name,
                'email': email,
                'subject': subject_text,
                'order_number': order_number,
                'message': message_body,
            }

            # Send notification email to admin
            try:
                admin_subject = f'[HENDOSHI Contact] {subject_text} from {name}'
                admin_message = render_to_string(
                    'home/emails/contact_admin_notification.txt',
                    email_context
                )
                admin_html = render_to_string(
                    'home/emails/contact_admin_notification.html',
                    email_context
                )

                admin_email = EmailMultiAlternatives(
                    subject=admin_subject,
                    body=admin_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[email],
                )
                admin_email.attach_alternative(admin_html, 'text/html')
                admin_email.send(fail_silently=False)
            except Exception:
                pass  # Log error in production

            # Send auto-reply confirmation email to customer
            try:
                customer_subject = 'We received your message - HENDOSHI'
                customer_message = render_to_string(
                    'home/emails/contact_customer_confirmation.txt',
                    email_context
                )
                customer_html = render_to_string(
                    'home/emails/contact_customer_confirmation.html',
                    email_context
                )

                customer_email = EmailMultiAlternatives(
                    subject=customer_subject,
                    body=customer_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                customer_email.attach_alternative(customer_html, 'text/html')
                customer_email.send(fail_silently=False)
            except Exception:
                pass  # Log error in production

            messages.success(
                request,
                'Your message has been sent! We\'ll get back to you soon.'
            )
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'home/contact.html', {'form': form})


def shipping(request):
    """
    View to display shipping information
    """
    return render(request, 'home/shipping.html')


def returns(request):
    """
    View to display returns information
    """
    return render(request, 'home/returns.html')


def size_guide(request):
    """
    View to display size guide information
    """
    return render(request, 'home/size_guide.html')


def faq(request):
    """
    View to display frequently asked questions
    """
    return render(request, 'home/faq.html')

def track_order(request):
    """
    View to handle order tracking
    """
    from checkout.models import Order
    
    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip()
        email = request.POST.get('email', '').strip()
        
        try:
            # Find order by order number and email
            order = Order.objects.get(
                order_number=order_number,
                email__iexact=email
            )
            # Redirect to order detail page
            return redirect('order_detail', order_number=order.order_number)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check your order number and email address.')
    
    return render(request, 'home/track_order.html')
