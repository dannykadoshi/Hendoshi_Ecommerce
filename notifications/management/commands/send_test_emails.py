from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from pathlib import Path
import re
import time
import fnmatch
from types import SimpleNamespace


class Command(BaseCommand):
    help = 'Render and send all email templates to a test recipient (prints to console if using console backend)'

    def add_arguments(self, parser):
        parser.add_argument('recipient', nargs='?', help='Recipient email address', default='admin@hendoshi.com')
        parser.add_argument('--throttle', type=float, default=0.0, help='Seconds to wait between sends (throttle to avoid rate limits)')
        parser.add_argument('--only', type=str, default='', help='Comma-separated list of template paths (relative to templates/) to send; if empty sends all')

    def handle(self, *args, **options):
        recipient = options['recipient']
        templates_dir = Path(settings.BASE_DIR) / 'templates'

        # Find all templates under any "emails" folder
        template_paths = sorted(templates_dir.rglob('*/emails/*.html'))
        only_patterns = [p.strip() for p in options.get('only', '').split(',') if p.strip()]
        if only_patterns:
            filtered = []
            for p in template_paths:
                rel = p.relative_to(templates_dir).as_posix()
                for pat in only_patterns:
                    if fnmatch.fnmatch(rel, pat):
                        filtered.append(p)
                        break
            template_paths = filtered
        if not template_paths:
            self.stdout.write(self.style.WARNING('No email templates found under templates/*/emails/*.html'))
            return

        # Minimal safe context for rendering templates
        ctx = {
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'user': SimpleNamespace(username='admin', first_name='Admin', email=recipient),
            'profile': {'name': 'Admin'},
            'product': SimpleNamespace(name='Demo Product', description='Demo description', main_image=SimpleNamespace(url='/media/demo-product.jpg')),
            'photo': SimpleNamespace(image=SimpleNamespace(url='/media/demo-photo.jpg'), caption='Demo caption', id=1),
            'cart_items': [],
            'cart_total': '$0.00',
            'checkout_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'unsubscribe_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'preferences_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'notification': {'price_drop_percentage': 20, 'original_price': '100.00', 'new_price': '80.00', 'price_savings': '20.00'},
            'product_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        sent = 0
        throttle = float(options.get('throttle', 0.0) or 0.0)
        for idx, full_path in enumerate(template_paths):
            # Render path relative to templates dir
            try:
                rel = full_path.relative_to(templates_dir).as_posix()
            except Exception:
                rel = full_path.name

            try:
                html = render_to_string(rel, ctx)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'Failed to render {rel}: {exc}'))
                continue

            # Try to extract a <title> from the HTML for a subject
            m = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            subject = m.group(1).strip() if m else f'Test email: {rel}'

            # Plain-text fallback: strip tags conservatively
            text = re.sub(r'<[^>]+>', '', html)

            msg = EmailMultiAlternatives(subject=subject, body=text, from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None), to=[recipient])
            msg.attach_alternative(html, 'text/html')

            try:
                msg.send()
                sent += 1
                self.stdout.write(self.style.SUCCESS(f'Sent {rel} -> {recipient} (subject: "{subject}")'))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'Error sending {rel} -> {recipient}: {exc}'))

            # throttle to avoid provider rate limits
            if throttle and idx < len(template_paths) - 1:
                time.sleep(throttle)

        self.stdout.write(self.style.NOTICE(f'Done. Attempted to send {len(template_paths)} templates, succeeded sends: {sent}'))
