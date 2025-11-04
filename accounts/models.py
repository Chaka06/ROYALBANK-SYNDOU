from django.db import models
from django.contrib.auth.models import User
import random

class Account(models.Model):
    STATUS_CHOICES = (
        ('active', 'Actif'),
        ('blocked', 'Bloqué'),
    )
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    display_name = models.CharField(max_length=150)
    balance_cents = models.BigIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active')
    debt_cents = models.BigIntegerField(default=0)
    can_transact = models.BooleanField(default=True)
    # Banking details - Format canadien
    account_number = models.CharField(max_length=20, blank=True)
    institution_number = models.CharField(max_length=3, blank=True)  # Institution (3 chiffres) - RBC = 003
    transit_number = models.CharField(max_length=5, blank=True)  # Transit (5 chiffres) - Numéro de succursale
    bank_name = models.CharField(max_length=100, default='Royal Bank of Canada')
    branch_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.institution_number:
            # Royal Bank of Canada institution number
            self.institution_number = "003"
        if not self.transit_number:
            # Transit number (5 chiffres) - numéro de succursale
            self.transit_number = f"{random.randint(10000, 99999)}"
        if not self.account_number:
            # Account number (7-12 chiffres) - format canadien
            self.account_number = f"{random.randint(1000000, 999999999999)}"
        if not self.branch_code:
            # Branch code (même que transit pour format canadien)
            self.branch_code = self.transit_number
        super().save(*args, **kwargs)

    def balance_display(self) -> str:
        return f"${self.balance_cents/100:,.2f}"

    def debt_display(self) -> str:
        return f"${self.debt_cents/100:,.2f}"

    def routing_number(self) -> str:
        """Format routier canadien : Institution + Transit"""
        return f"{self.institution_number}-{self.transit_number}"

    def formatted_account_number(self) -> str:
        """Format account number avec espaces pour lisibilité"""
        if not self.account_number:
            return ""
        # Format: XXXX XXXX XXXX (groupes de 4)
        account = self.account_number.replace(' ', '')
        return ' '.join([account[i:i+4] for i in range(0, len(account), 4)])

    def __str__(self) -> str:
        return f"Compte de {self.display_name}"


class Card(models.Model):
    TYPE_CHOICES = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
    )
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='card')
    card_number = models.CharField(max_length=16)
    cardholder_name = models.CharField(max_length=100)
    expiry_month = models.IntegerField()
    expiry_year = models.IntegerField()
    cvv = models.CharField(max_length=4)
    card_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='VISA')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def masked_number(self) -> str:
        """Return masked card number (**** **** **** 1234)"""
        if len(self.card_number) >= 4:
            return f"**** **** **** {self.card_number[-4:]}"
        return "**** **** **** ****"

    def formatted_expiry(self) -> str:
        """Return formatted expiry (MM/YY)"""
        return f"{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}"

    def __str__(self) -> str:
        return f"{self.card_type} - {self.masked_number()}"
