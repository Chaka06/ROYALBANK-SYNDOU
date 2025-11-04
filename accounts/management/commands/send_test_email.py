from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from sphinx.email_utils import send_email


class Command(BaseCommand):
    help = 'Send a test email using the configured email backend.'

    def add_arguments(self, parser):
        parser.add_argument('--to', dest='to', required=True, help='Recipient email address')
        parser.add_argument('--subject', dest='subject', default='Email de test', help='Email subject')
        parser.add_argument('--message', dest='message', default='Ceci est un email de test de ROYAL.', help='Email body')

    def handle(self, *args, **options):
        to = options['to']
        subject = options['subject']
        message = options['message']
        if not to:
            raise CommandError('Veuillez fournir une adresse avec --to')

        ok = send_email(subject=subject, message=message, to=[to], fail_silently=True)
        if ok:
            self.stdout.write(self.style.SUCCESS(f"Email envoyé à {to} depuis {getattr(settings, 'DEFAULT_FROM_EMAIL', 'non défini')}"))
        else:
            self.stdout.write(self.style.WARNING(
                "Échec envoi SMTP. Un log de secours a pu être écrit dans tmp/emails/."
            ))

