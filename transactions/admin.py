from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("owner", "created_at", "amount_cents", "status", "beneficiary_name")
    list_filter = ("status",)
    search_fields = ("beneficiary_name", "beneficiary_iban")
