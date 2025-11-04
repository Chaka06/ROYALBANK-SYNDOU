from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("owner", "created_at", "amount_display", "status", "beneficiary_name", "description")
    list_filter = ("status", "created_at")
    search_fields = ("beneficiary_name", "beneficiary_iban", "description")
    date_hierarchy = "created_at"
    fields = ("owner", "created_at", "amount_cents", "description", "status", "beneficiary_name", "beneficiary_iban")
