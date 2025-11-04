from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update a superuser (non-interactive)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the superuser')
        parser.add_argument('password', type=str, help='Password for the superuser')
        parser.add_argument('--email', type=str, default='', help='Email address (optional)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options.get('email', '')

        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Only update password if user doesn't have a password set (new user)
            # This preserves existing passwords between deployments
            if not user.has_usable_password():
                user.set_password(password)
                self.stdout.write(self.style.WARNING(f'⚠ Mot de passe défini pour "{username}" (aucun mot de passe existant)'))
            # Ensure superuser and staff rights
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                self.stdout.write(self.style.SUCCESS(f'✓ Droits superuser activés pour "{username}"'))
            if email and user.email != email:
                user.email = email
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Superuser "{username}" existe déjà (données préservées)')
            )
        else:
            # Create new superuser
            User.objects.create_superuser(
                username=username,
                email=email or f'{username}@rbc-bank.com',
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Superuser "{username}" créé avec succès!')
            )

        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email or f"{username}@rbc-bank.com"}')
        self.stdout.write(f'  Accès admin: https://rbc-bank.com/admin/')

