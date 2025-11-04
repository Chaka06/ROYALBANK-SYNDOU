from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account


class Command(BaseCommand):
    help = 'Create user or reset password if exists'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('password', type=str, help='Password')
        parser.add_argument('--email', type=str, default='', help='Email address')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options.get('email', '')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_active': True,
            }
        )
        
        # Set password (always update it)
        user.set_password(password)
        if email:
            user.email = email
        user.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Utilisateur {username} créé avec succès')
            )
            # Create account if it doesn't exist
            account, acc_created = Account.objects.get_or_create(
                owner=user,
                defaults={
                    'display_name': user.username,
                    'balance_cents': 0,
                }
            )
            if acc_created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Compte bancaire créé pour {username}')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Mot de passe mis à jour pour {username}')
            )
        
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        if email:
            self.stdout.write(f'  Email: {email}')

