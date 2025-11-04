from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'List all users'

    def handle(self, *args, **options):
        users = User.objects.all()
        if users.exists():
            self.stdout.write('=== Utilisateurs existants ===')
            for user in users:
                email_str = user.email if user.email else 'AUCUN'
                self.stdout.write(f'  - {user.username} ({email_str})')
        else:
            self.stdout.write(self.style.WARNING('Aucun utilisateur trouvé'))

