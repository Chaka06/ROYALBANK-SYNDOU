from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    STATUS = (
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Effectuée'),
        ('REJECTED', 'Rejetée'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    amount_cents = models.BigIntegerField()
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=STATUS)
    beneficiary_name = models.CharField(max_length=150, blank=True)
    beneficiary_iban = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['-created_at']

    def amount_display(self) -> str:
        return f"${self.amount_cents/100:,.2f}"

    def transaction_number(self) -> str:
        """Generate a transaction reference number"""
        return f"742764{self.id:06d}"

    def __str__(self) -> str:
        return f"{self.description or 'Transaction'} - {self.amount_display()}"
