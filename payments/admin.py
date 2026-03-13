from django.contrib import admin
from .models import (
    CoursePayment,
    TeacherEarning,
    TeacherSalaryBalance,
    SalaryWithdrawal,
)


@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course',
        'total_amount', 'per_lesson_amount',
        'status', 'paid_at'
    ]
    list_filter = ['status', 'course']
    search_fields = [
        'student__student_id',
        'student__user__first_name',
    ]
    readonly_fields = ['created_at', 'per_lesson_amount']


@admin.register(TeacherEarning)
class TeacherEarningAdmin(admin.ModelAdmin):
    list_display = [
        'teacher', 'course',
        'students_present',
        'total_lesson_amount',
        'teacher_share',
        'system_share',
        'created_at',
    ]
    list_filter = ['course', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(TeacherSalaryBalance)
class TeacherSalaryBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'teacher',
        'current_month_earning',
        'total_earning',
        'month',
        'last_updated',
    ]
    readonly_fields = ['last_updated']
    ordering = ['-current_month_earning']


@admin.register(SalaryWithdrawal)
class SalaryWithdrawalAdmin(admin.ModelAdmin):
    list_display = [
        'teacher', 'amount',
        'status', 'requested_at', 'processed_at'
    ]
    list_filter = ['status']
    readonly_fields = ['requested_at']

    # Admin dan to'g'ridan tasdiqlash tugmasi
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        from .services import approve_withdrawal
        approved = 0
        for withdrawal in queryset.filter(status='pending'):
            try:
                approve_withdrawal(withdrawal)
                approved += 1
            except ValueError:
                pass
        self.message_user(
            request,
            f"{approved} ta so'rov tasdiqlandi!"
        )
    approve_selected.short_description = "Tanlangan so'rovlarni tasdiqlash"