from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("display_name", "balance_cents", "status", "debt_cents", "can_transact", "updated_at")
    list_filter = ("status", "can_transact")
    search_fields = ("display_name",)
