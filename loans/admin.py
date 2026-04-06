from django.contrib import admin

from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "status", "issued_at", "due_date", "returned_at")
    list_filter = ("status",)
    raw_id_fields = ("book", "user")
