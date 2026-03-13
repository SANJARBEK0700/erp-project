from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import (
    CoursePayment,
    TeacherEarning,
    TeacherSalaryBalance,
    SalaryWithdrawal,
)
from .services import request_withdrawal, approve_withdrawal
from apps.teachers.models import Teacher


@login_required
def teacher_salary_detail(request, teacher_id):
    """
    O'qituvchining oylik hisobi — batafsil
    """
    teacher = get_object_or_404(Teacher, pk=teacher_id)

    # Joriy oylik balans
    balance = getattr(teacher, 'salary_balance', None)

    # Dars bo'yicha daromadlar tarixi
    earnings = teacher.earnings.select_related(
        'course', 'attendance'
    ).order_by('-created_at')

    # Oylar bo'yicha guruhlab ko'rsatish
    monthly_summary = teacher.earnings.values(
        'created_at__year',
        'created_at__month',
    ).annotate(
        total=Sum('teacher_share')
    ).order_by('-created_at__year', '-created_at__month')

    # Oylik so'rovlar tarixi
    withdrawals = teacher.withdrawals.order_by('-requested_at')

    context = {
        'teacher': teacher,
        'balance': balance,
        'earnings': earnings,
        'monthly_summary': monthly_summary,
        'withdrawals': withdrawals,
    }
    return render(request, 'payments/teacher_salary.html', context)


@login_required
def request_salary_withdrawal(request, teacher_id):
    """
    O'qituvchi oylik olish so'rovi yuborishi
    """
    teacher = get_object_or_404(Teacher, pk=teacher_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '0')

        try:
            from decimal import Decimal
            amount = Decimal(amount_str)
            request_withdrawal(teacher, amount)
            messages.success(
                request,
                f"{amount} so'm olish so'rovi yuborildi! "
                f"Admin tasdiqlashini kuting."
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('payments:teacher_salary', teacher_id=teacher.pk)

    balance = getattr(teacher, 'salary_balance', None)
    return render(request, 'payments/request_withdrawal.html', {
        'teacher': teacher,
        'balance': balance,
    })


@login_required
def approve_salary_withdrawal(request, withdrawal_id):
    """
    Admin oylik so'rovini tasdiqlaydi
    """
    withdrawal = get_object_or_404(SalaryWithdrawal, pk=withdrawal_id)

    if request.method == 'POST':
        try:
            approve_withdrawal(withdrawal)
            messages.success(
                request,
                f"{withdrawal.teacher} uchun "
                f"{withdrawal.amount} so'm to'landi!"
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('payments:withdrawal_list')

    return render(request, 'payments/approve_withdrawal.html', {
        'withdrawal': withdrawal,
    })


@login_required
def withdrawal_list(request):
    """
    Barcha oylik so'rovlar — Admin uchun
    """
    withdrawals = SalaryWithdrawal.objects.select_related(
        'teacher', 'teacher__user'
    ).order_by('-requested_at')

    # Faqat kutilayotganlar
    status = request.GET.get('status', 'pending')
    if status:
        withdrawals = withdrawals.filter(status=status)

    return render(request, 'payments/withdrawal_list.html', {
        'withdrawals': withdrawals,
        'selected_status': status,
        'status_choices': SalaryWithdrawal.STATUS_CHOICES,
    })


@login_replace
def course_payment_list(request):
    """
    Barcha kurs to'lovlari — Admin uchun
    """
    payments = CoursePayment.objects.select_related(
        'student', 'student__user', 'course'
    ).order_by('-created_at')

    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)

    return render(request, 'payments/course_payment_list.html', {
        'payments': payments,
        'status_choices': CoursePayment.STATUS_CHOICES,
        'selected_status': status,
    })

# Mavjud viewlarga QO'SHIMCHA

from .forms import CoursePaymentCreateForm, MakePaymentForm
from .services import create_course_payment, make_payment, get_student_payment_summary
from apps.students.models import Student


@login_required
def student_payments(request, student_id):
    """
    O'quvchining barcha to'lovlari — student o'zi yoki Admin ko'radi
    """
    student = get_object_or_404(Student, pk=student_id)
    summary = get_student_payment_summary(student)

    return render(request, 'payments/student_payments.html', {
        'student': student,
        'payments': summary['payments'],
        'total_amount': summary['total_amount'],
        'total_paid': summary['total_paid'],
        'remaining': summary['remaining'],
    })


@login_required
def payment_detail(request, payment_id):
    """
    Bitta to'lov tafsiloti — barcha tranzaksiyalar
    """
    payment = get_object_or_404(CoursePayment, pk=payment_id)

    # Barcha to'lov tranzaksiyalari
    transactions = payment.transactions.order_by('-created_at')

    # Qolgan summa
    from django.db.models import Sum
    paid = transactions.filter(
        status='success'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    remaining = payment.total_amount - paid

    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
        'transactions': transactions,
        'paid': paid,
        'remaining': remaining,
    })


@login_required
def make_payment_view(request, payment_id):
    """
    To'lov qilish sahifasi — Admin qabul qiladi
    """
    payment = get_object_or_404(CoursePayment, pk=payment_id)
    form = MakePaymentForm(course_payment=payment)

    if request.method == 'POST':
        form = MakePaymentForm(payment, request.POST)
        if form.is_valid():
            try:
                make_payment(
                    course_payment=payment,
                    amount=form.cleaned_data['amount'],
                    payment_method=form.cleaned_data['payment_method'],
                    received_by=request.user,
                    note=form.cleaned_data.get('note', ''),
                )
                messages.success(
                    request,
                    f"{form.cleaned_data['amount']} so'm "
                    f"muvaffaqiyatli qabul qilindi!"
                )
                return redirect('payments:payment_detail', payment_id=payment.pk)
            except ValueError as e:
                messages.error(request, str(e))

    return render(request, 'payments/make_payment.html', {
        'payment': payment,
        'form': form,
    })


@login_required
def create_course_payment_view(request):
    """
    Admin tomonidan o'quvchiga to'lov belgilash
    """
    if request.method == 'POST':
        form = CoursePaymentCreateForm(request.POST)
        if form.is_valid():
            try:
                payment, created = create_course_payment(
                    student=form.cleaned_data['student'],
                    course=form.cleaned_data['course'],
                    total_amount=form.cleaned_data['total_amount'],
                )
                if created:
                    messages.success(
                        request,
                        f"To'lov muvaffaqiyatli yaratildi! "
                        f"Har dars: {payment.per_lesson_amount} so'm"
                    )
                else:
                    messages.warning(
                        request,
                        "Bu o'quvchi uchun to'lov allaqachon mavjud!"
                    )
                return redirect(
                    'payments:payment_detail',
                    payment_id=payment.pk
                )
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = CoursePaymentCreateForm()

    return render(request, 'payments/create_payment.html', {'form': form})