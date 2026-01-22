from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import os


class Command(BaseCommand):
    help = 'Visualize email templates in terminal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template',
            type=str,
            choices=['admin', 'customer', 'all'],
            default='all',
            help='Which email template to visualize (admin, customer, or all)'
        )

    def handle(self, *args, **options):
        # Sample data for rendering templates
        sample_context = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'Order Issue',
            'order_number': 'ORD-12345',
            'message': 'I received the wrong item in my order. I ordered a blue hoodie but received a red one. Please help me resolve this issue.',
        }

        template_choice = options['template']

        if template_choice in ['admin', 'all']:
            self.stdout.write(self.style.SUCCESS('\n' + '='*80))
            self.stdout.write(self.style.SUCCESS('ADMIN NOTIFICATION EMAIL'))
            self.stdout.write(self.style.SUCCESS('='*80))

            # Render admin email templates
            admin_subject = f'[HENDOSHI Contact] {sample_context["subject"]} from {sample_context["name"]}'

            admin_txt = render_to_string('home/emails/contact_admin_notification.txt', sample_context)
            admin_html = render_to_string('home/emails/contact_admin_notification.html', sample_context)

            self.stdout.write(f'\nSubject: {admin_subject}')
            self.stdout.write('\nTEXT VERSION:')
            self.stdout.write('-'*40)
            self.stdout.write(admin_txt)

            self.stdout.write('\nHTML VERSION (rendered as text):')
            self.stdout.write('-'*40)
            # Strip HTML tags for terminal display
            import re
            html_clean = re.sub(r'<[^>]+>', '', admin_html)
            html_clean = re.sub(r'\n\s*\n', '\n', html_clean)  # Remove extra newlines
            self.stdout.write(html_clean)

        if template_choice in ['customer', 'all']:
            self.stdout.write(self.style.SUCCESS('\n' + '='*80))
            self.stdout.write(self.style.SUCCESS('CUSTOMER CONFIRMATION EMAIL'))
            self.stdout.write(self.style.SUCCESS('='*80))

            # Render customer email templates
            customer_subject = 'We received your message - HENDOSHI'

            customer_txt = render_to_string('home/emails/contact_customer_confirmation.txt', sample_context)
            customer_html = render_to_string('home/emails/contact_customer_confirmation.html', sample_context)

            self.stdout.write(f'\nSubject: {customer_subject}')
            self.stdout.write('\nTEXT VERSION:')
            self.stdout.write('-'*40)
            self.stdout.write(customer_txt)

            self.stdout.write('\nHTML VERSION (rendered as text):')
            self.stdout.write('-'*40)
            # Strip HTML tags for terminal display
            import re
            html_clean = re.sub(r'<[^>]+>', '', customer_html)
            html_clean = re.sub(r'\n\s*\n', '\n', html_clean)  # Remove extra newlines
            self.stdout.write(html_clean)

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('Email visualization complete!'))
        self.stdout.write(self.style.SUCCESS('='*80))