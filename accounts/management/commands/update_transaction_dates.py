from django.core.management.base import BaseCommand
from transactions.models import Transaction
from django.utils import timezone
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Update transaction dates to 10/03/2025'

    def handle(self, *args, **options):
        # Date cible: 10 mars 2025
        target_date = datetime(2025, 3, 10, 14, 30, 0)
        target_date = timezone.make_aware(target_date)
        
        # Récupérer toutes les transactions et les mettre à jour
        transactions = Transaction.objects.all().order_by('-created_at')
        
        if not transactions.exists():
            self.stdout.write(self.style.WARNING('Aucune transaction trouvée.'))
            return
        
        # Mettre à jour chaque transaction avec une date différente
        for i, tx in enumerate(transactions):
            # Différentes heures pour chaque transaction
            new_date = target_date - timedelta(hours=i)
            tx.created_at = new_date
            tx.save()
            self.stdout.write(
                self.style.SUCCESS(f'Transaction {tx.id} mise à jour: {new_date.strftime("%d/%m/%Y %H:%M")}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'{transactions.count()} transaction(s) mise(s) à jour avec la date 10/03/2025')
        )

