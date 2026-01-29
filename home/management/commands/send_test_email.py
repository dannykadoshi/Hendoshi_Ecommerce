from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send a test email using Resend'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        recipient = options['email']

        result = send_mail(
            subject='Test Email from HENDOSHI Django Site',
            message='This is a test email sent from your Django application using Resend integration.',
            from_email='HENDOSHI <noreply@mail.hendoshi.com>',
            recipient_list=[recipient],
            html_message='<h2>Test Email from HENDOSHI</h2><p>This is a test email sent from your Django application using <strong>Resend</strong> integration.</p><p>If you received this, your email configuration is working correctly!</p>'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Test email sent successfully to {recipient}! Result: {result}')
        )