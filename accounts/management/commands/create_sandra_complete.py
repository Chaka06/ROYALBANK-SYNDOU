from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account
from transactions.models import Transaction
from notifications.models import Notification
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Create sandra763 user with all complete information from local database'

    def handle(self, *args, **options):
        username = 'sandra763'
        password = '01254533'
        
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'pelletiersandra138@gmail.com',
                'first_name': 'Sandra',
                'last_name': 'Pelletier',
                'is_active': True,
            }
        )
        
        # Only update password if user doesn't have a password set (preserves existing passwords)
        if not user.has_usable_password():
            user.set_password(password)
            self.stdout.write(self.style.WARNING(f'⚠ Mot de passe défini pour {username} (aucun mot de passe existant)'))
        # Always update other fields
        user.email = 'pelletiersandra138@gmail.com'
        user.first_name = 'Sandra'
        user.last_name = 'Pelletier'
        user.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Utilisateur {username} créé'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Utilisateur {username} mis à jour'))
        
        # Create or update account with exact values
        account, acc_created = Account.objects.get_or_create(
            owner=user,
            defaults={
                'display_name': 'Sandra Pelletier',
                'balance_cents': 215000000,  # $2,150,000.00
                'debt_cents': 5721750,  # $57,217.50
                'status': 'active',
                'can_transact': False,  # Can't transact due to debt
                'bank_name': 'ROYAL BANK',
                'institution_number': '003',
                'transit_number': '71137',
                'account_number': '678137269603',
                'branch_code': '65561',
            }
        )
        
        # Update account if it already exists
        if not acc_created:
            account.display_name = 'Sandra Pelletier'
            account.balance_cents = 215000000
            account.debt_cents = 5721750
            account.status = 'active'
            account.can_transact = False
            account.bank_name = 'ROYAL BANK'
            account.institution_number = '003'
            account.transit_number = '71137'
            account.account_number = '678137269603'
            account.branch_code = '65561'
            account.save()
        
        if acc_created:
            self.stdout.write(self.style.SUCCESS('✓ Compte bancaire créé'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Compte bancaire mis à jour'))
        
        self.stdout.write(f'  Solde: {account.balance_display()}')
        self.stdout.write(f'  Dettes: {account.debt_display()}')
        self.stdout.write(f'  Numéro de compte: {account.formatted_account_number()}')
        self.stdout.write(f'  Numéro de routage: {account.routing_number()}')
        
        # Card creation removed - user doesn't want Visa cards
        
        # Create a sample transaction if none exist
        if not Transaction.objects.filter(owner=user).exists():
            Transaction.objects.create(
                owner=user,
                created_at=pytz.timezone('America/Toronto').localize(datetime(2025, 3, 10, 14, 30, 0)),
                amount_cents=150000,  # $1,500.00
                description="Virement entrant - Salaire",
                status="COMPLETED",
                beneficiary_name="Employeur XYZ",
                beneficiary_iban="CA12345678901234567890"
            )
            self.stdout.write(self.style.SUCCESS('✓ Transaction exemple créée'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Transactions existantes, aucune nouvelle transaction créée'))
        
        # Create a sample notification if none exist
        if not Notification.objects.filter(user=user).exists():
            Notification.objects.create(
                user=user,
                title="Bienvenue sur ROYAL Bank",
                body="Votre compte bancaire en ligne est maintenant actif. Vous pouvez gérer vos finances en toute sécurité.",
                is_read=False
            )
            self.stdout.write(self.style.SUCCESS('✓ Notification exemple créée'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Notifications existantes, aucune nouvelle notification créée'))
        
        self.stdout.write(f'\n✓ Compte complet créé/mis à jour avec succès!')
        self.stdout.write(f'\nIdentifiants:')
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Email: {user.email}')

