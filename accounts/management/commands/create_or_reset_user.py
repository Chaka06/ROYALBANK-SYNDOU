from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account
# Card import removed - card feature disabled
import random


class Command(BaseCommand):
    help = 'Create user with complete account setup or reset password if exists'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('password', type=str, help='Password')
        parser.add_argument('--email', type=str, default='', help='Email address')
        parser.add_argument('--balance', type=float, default=5000.00, help='Initial balance (default: 5000.00)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options.get('email', '')
        balance = options.get('balance', 5000.00)
        
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
            
            # Create account with Canadian banking details
            account, acc_created = Account.objects.get_or_create(
                owner=user,
                defaults={
                    'display_name': user.username.upper(),
                    'balance_cents': int(balance * 100),  # Convert to cents
                    'status': 'active',
                    'can_transact': True,
                    'bank_name': 'Royal Bank of Canada',
                    'institution_number': '003',
                    'transit_number': f"{random.randint(10000, 99999)}",
                    'account_number': f"{random.randint(1000000, 999999999999)}",
                }
            )
            
            if acc_created:
                # Save again to ensure banking details are generated
                account.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Compte bancaire créé pour {username}')
                )
                self.stdout.write(f'  Solde initial: ${balance:,.2f}')
                self.stdout.write(f'  Numéro de compte: {account.formatted_account_number()}')
                self.stdout.write(f'  Numéro de routage: {account.routing_number()}')
                
                # Card creation removed - card feature disabled
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Compte bancaire existe déjà pour {username}')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Mot de passe mis à jour pour {username}')
            )
            # Check if account exists
            try:
                account = user.account
                self.stdout.write(f'  Compte existant - Solde: {account.balance_display()}')
            except Account.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Aucun compte bancaire trouvé pour {username}')
                )
        
        self.stdout.write(f'\nIdentifiants:')
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        if email:
            self.stdout.write(f'  Email: {email}')

