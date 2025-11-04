import socket
from django.core.management.base import BaseCommand
from django.conf import settings
from sphinx.email_utils import send_email


class Command(BaseCommand):
    help = 'Diagnose SMTP configuration: prints settings, tests TCP connectivity, and sends a test email.'

    def add_arguments(self, parser):
        parser.add_argument('--to', dest='to', required=True, help='Recipient email address for the test email')

    def handle(self, *args, **options):
        to = options['to']

        self.stdout.write('--- Email settings (effective) ---')
        fields = [
            'EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER',
            'EMAIL_USE_TLS', 'EMAIL_USE_SSL', 'EMAIL_TIMEOUT', 'DEFAULT_FROM_EMAIL'
        ]
        for f in fields:
            self.stdout.write(f"{f}: {getattr(settings, f, None)}")

        host = getattr(settings, 'EMAIL_HOST', None)
        port = int(getattr(settings, 'EMAIL_PORT', 0) or 0)
        if host and port:
            self.stdout.write('\n--- TCP connectivity test ---')
            try:
                with socket.create_connection((host, port), timeout=10):
                    self.stdout.write(self.style.SUCCESS(f"OK: TCP connection to {host}:{port}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"FAIL: Cannot connect to {host}:{port} -> {e}"))
        else:
            self.stdout.write(self.style.WARNING('EMAIL_HOST/EMAIL_PORT not set; SMTP will not be used.'))

        self.stdout.write('\n--- Send test email ---')
        ok = send_email(
            subject='Test SMTP - ROYAL',
            message='Test SMTP depuis la commande check_email.',
            to=[to],
            fail_silently=True,
        )
        if ok:
            self.stdout.write(self.style.SUCCESS(f"Email envoyé à {to}"))
        else:
            self.stdout.write(self.style.ERROR(
                'Échec envoi. Vérifiez les identifiants, le port et TLS/SSL. Un log fallback peut être écrit dans tmp/emails/.'))


