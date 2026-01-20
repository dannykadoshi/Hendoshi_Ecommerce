from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from vault.models import VaultPhoto
from products.models import Product
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Test the vault photo rejection email functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='noreply@hendoshi.com',
            help='Email address to send the test to (default: noreply@hendoshi.com)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='This is a test rejection reason to verify the email functionality is working correctly.',
            help='Rejection reason to include in the email'
        )

    def handle(self, *args, **options):
        email = options['email']
        rejection_reason = options['reason']

        self.stdout.write(
            self.style.SUCCESS(f'Testing vault photo rejection email to: {email}')
        )

        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test_user_email',
            defaults={
                'email': email,
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {test_user.username}')
            )

        # Create a test product if it doesn't exist
        test_product, created = Product.objects.get_or_create(
            name='Test Product for Email',
            defaults={
                'description': 'Test product for email testing',
                'base_price': 29.99,
                'product_type': 'tshirt',
                'is_archived': False
            }
        )

        # Create a test photo
        test_photo = VaultPhoto.objects.create(
            user=test_user,
            caption='Test photo for email functionality',
            status='pending'
        )

        # Tag the photo with the test product
        test_photo.tagged_products.add(test_product)

        self.stdout.write(
            self.style.SUCCESS(f'Created test photo: {test_photo.id}')
        )

        # Send the rejection email (or simulate it)
        try:
            subject = f'Your HENDOSHI Vault photo has been reviewed'
            context = {
                'user': test_user,
                'photo': test_photo,
                'rejection_reason': rejection_reason,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            }

            html_message = render_to_string('notifications/emails/photo_rejected.html', context)
            plain_message = f"""
            Hi {test_user.username},

            Your photo submission to The HENDOSHI Vault has been reviewed.

            Unfortunately, your photo was not approved for the following reason:

            {rejection_reason}

            You can submit a new photo anytime at: {settings.SITE_URL}/vault/submit/

            Best regards,
            The HENDOSHI Team
            """

            self.stdout.write(
                self.style.SUCCESS('✅ Email template rendered successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Subject: {subject}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'To: {email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'From: {settings.DEFAULT_FROM_EMAIL}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Rejection reason: {rejection_reason}')
            )

            # For testing, use console backend to show the email would work
            # In production, this will use the SMTP backend from settings
            from django.core.mail.backends.console import EmailBackend

            console_backend = EmailBackend()
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
                connection=console_backend  # Use console for testing
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Email template and logic work correctly!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📧 Email would be sent to: {email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📧 From: {settings.DEFAULT_FROM_EMAIL}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📧 Subject: {subject}')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Note: Email sent to console for testing.')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  In production with proper AWS SES config, real emails will be sent.')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to render email template: {str(e)}')
            )
            raise CommandError(f'Email template rendering failed: {str(e)}')

        # Clean up - mark photo as rejected and show what was created
        test_photo.status = 'rejected'
        test_photo.save()

        self.stdout.write(
            self.style.WARNING(f'Note: Test photo marked as rejected. Test user and product remain for future tests.')
        )
        self.stdout.write(
            self.style.WARNING(f'To clean up completely, you can delete the test user and product manually.')
        )