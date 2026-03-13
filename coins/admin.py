from django.contrib import admin
from .models import CoinBalance, CoinTransaction


@admin.register(CoinBalance)
class CoinBalanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'total_coins', 'updated_at']
    search_fields = ['student__student_id', 'student__user__first_name']
    ordering = ['-total_coins']


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'reason', 'description', 'created_at']
    list_filter = ['reason', 'created_at']
    search_fields = ['student__student_id']
    readonly_fields = ['created_at']