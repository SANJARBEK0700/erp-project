from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# O'qituvchiga tushadigan foiz
TEACHER_SHARE_PERCENT = Decimal('0.50')  # 50%


def calculate_per_lesson_amount(course_payment):
    """
    Har bir dars narxini hisoblash:
    per_lesson = total_amount / kurs davomidagi jami darslar soni
    """
    from apps.schedule.models import Schedule

    # Kurs necha marta dars o'tadi (jadval asosida)
    total_lessons = Schedule.objects.filter(
        course=course_payment.course,
        is_active=True
    ).count()

    if total_lessons == 0:
        return Decimal('0')

    per_lesson = course_payment.total_amount / total_lessons
    return round(per_lesson, 2)


def process_lesson_payment(attendance_obj):
    """
    Davomat belgilanganida to'lov hisob-kitobi:
    1. O'sha darsga kelgan o'quvchilarning per_lesson summasi yig'iladi
    2. 50% o'qituvchiga, 50% tizimga

    attendance_obj — Attendance modeli (bitta o'quvchining davomati)
    """
    from .models import (
        CoursePayment,
        TeacherEarning,
        TeacherSalaryBalance,
    )
    from apps.attendance.models import Attendance

    course = attendance_obj.course
    teacher = attendance_obj.marked_by
    date = attendance_obj.date

    if teacher is None:
        return  # O'qituvchi yo'q — hisob-kitob qilinmaydi

    # Faqat bir marta hisob-kitob qilish uchun tekshirish
    # Bir darsda ko'p o'quvchi belgilanadi — faqat birinchisida ishlaydi
    if TeacherEarning.objects.filter(
            attendance=attendance_obj
    ).exists():
        return

    # Shu kun, shu kursga kelgan barcha o'quvchilar
    present_attendances = Attendance.objects.filter(
        course=course,
        date=date,
        status__in=['present', 'late']
        # late ham yarim hisob
    )

    # Har kelgan o'quvchidan per_lesson_amount yig'ish
    total_lesson_amount = Decimal('0')

    for att in present_attendances:
        try:
            payment = CoursePayment.objects.get(
                student=att.student,
                course=course,
                status='paid'  # faqat to'lagan o'quvchilar
            )
            if att.status == 'present':
                total_lesson_amount += payment.per_lesson_amount
            elif att.status == 'late':
                # Kech kelgan — yarim to'lov
                total_lesson_amount += payment.per_lesson_amount * Decimal('0.5')
        except CoursePayment.DoesNotExist:
            # To'lov qilmagan o'quvchi — hisobga olinmaydi
            continue

    if total_lesson_amount == 0:
        return

    # 50% / 50% hisoblash
    teacher_share = round(total_lesson_amount * TEACHER_SHARE_PERCENT, 2)
    system_share = total_lesson_amount - teacher_share

    with transaction.atomic():
        # TeacherEarning — bir dars uchun daromad yozuvi
        TeacherEarning.objects.create(
            teacher=teacher,
            course=course,
            attendance=attendance_obj,
            students_present=present_attendances.count(),
            total_lesson_amount=total_lesson_amount,
            teacher_share=teacher_share,
            system_share=system_share,
        )

        # TeacherSalaryBalance — oylik balansni yangilash
        current_month = timezone.now().strftime('%Y-%m')

        balance, created = TeacherSalaryBalance.objects.get_or_create(
            teacher=teacher,
            defaults={
                'current_month_earning': Decimal('0'),
                'total_earning': Decimal('0'),
                'month': current_month,
            }
        )

        # Oy o'zgarganmi? — reset qilish
        if balance.month != current_month:
            balance.current_month_earning = Decimal('0')
            balance.month = current_month

        balance.current_month_earning += teacher_share
        balance.total_earning += teacher_share
        balance.save()


def request_withdrawal(teacher, amount):
    """
    O'qituvchi oylik olish so'rovi
    """
    from .models import TeacherSalaryBalance, SalaryWithdrawal

    try:
        balance = TeacherSalaryBalance.objects.get(teacher=teacher)
    except TeacherSalaryBalance.DoesNotExist:
        raise ValueError("Balans topilmadi!")

    if amount > balance.current_month_earning:
        raise ValueError(
            f"Yetarli mablag' yo'q! "
            f"Joriy balans: {balance.current_month_earning} so'm"
        )

    with transaction.atomic():
        SalaryWithdrawal.objects.create(
            teacher=teacher,
            amount=amount,
        )
        # Balansdan ayirish — tasdiqlangandan keyin
        # Hozircha pending — admin tasdiqlaganda ayiriladi


def approve_withdrawal(withdrawal_obj):
    """
    Admin tomonidan oylik so'rovini tasdiqlash
    """
    from .models import TeacherSalaryBalance
    from django.utils import timezone

    with transaction.atomic():
        balance = TeacherSalaryBalance.objects.get(
            teacher=withdrawal_obj.teacher
        )

        if withdrawal_obj.amount > balance.current_month_earning:
            raise ValueError("Yetarli mablag' yo'q!")

        balance.current_month_earning -= withdrawal_obj.amount
        balance.save()

        withdrawal_obj.status = 'paid'
        withdrawal_obj.processed_at = timezone.now()
        withdrawal_obj.save()

# Mavjud funksiyalarga QO'SHIMCHA

import uuid
from decimal import Decimal


def create_course_payment(student, course, total_amount):
    """
    O'quvchi kursga yozilganida CoursePayment yaratish.
    Courses app dagi Enrollment signal chaqiradi.
    """
    from .models import CoursePayment

    # Allaqachon to'lov bor bo'lsa — qayta yaratmaslik
    payment, created = CoursePayment.objects.get_or_create(
        student=student,
        course=course,
        defaults={
            'total_amount': total_amount,
            'status': 'pending',
        }
    )

    if created:
        # per_lesson_amount hisoblash
        per_lesson = calculate_per_lesson_amount(payment)
        payment.per_lesson_amount = per_lesson
        payment.save()

    return payment, created


def make_payment(course_payment, amount, payment_method, received_by=None, note=''):
    """
    O'quvchi to'lov qilishi — asosiy funksiya.

    Agar to'langan summa yetarli bo'lsa — status 'paid' ga o'tadi.
    Bo'lib to'lashni ham qo'llab-quvvatlaydi.
    """
    from .models import PaymentTransaction
    from django.utils import timezone

    # Allaqachon to'liq to'langan bo'lsa
    if course_payment.status == 'paid':
        raise ValueError("Bu kurs allaqachon to'liq to'langan!")

    # Hozirga qadar to'langan jami summa
    already_paid = course_payment.transactions.filter(
        status='success'
    ).aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')

    # Qolgan summa
    remaining = course_payment.total_amount - already_paid

    if amount > remaining:
        raise ValueError(
            f"To'lov summasi qoldiqdan oshib ketdi! "
            f"Qolgan summa: {remaining} so'm"
        )

    # Chek raqami avtomatik generatsiya
    receipt_number = str(uuid.uuid4())[:8].upper()

    with transaction.atomic():
        # Transaction yozuvi
        payment_transaction = PaymentTransaction.objects.create(
            course_payment=course_payment,
            amount=amount,
            payment_method=payment_method,
            status='success',
            receipt_number=receipt_number,
            received_by=received_by,
            note=note,
        )

        # Jami to'langan summani qayta hisoblash
        total_paid = already_paid + amount

        # To'liq to'landimi?
        if total_paid >= course_payment.total_amount:
            course_payment.status = 'paid'
            course_payment.paid_at = timezone.now()
            course_payment.save()

            # Bildirishnoma
            from apps.notifications.models import Notification
            Notification.objects.create(
                recipient=course_payment.student.user,
                title=f"To'lov qabul qilindi",
                message=(
                    f"{course_payment.course.title} kursi uchun "
                    f"to'lov muvaffaqiyatli amalga oshirildi! "
                    f"Jami: {course_payment.total_amount} so'm"
                ),
                notif_type='system',
            )

    return payment_transaction


def get_student_payment_summary(student):
    """
    O'quvchining barcha to'lovlari bo'yicha xulosa
    """
    from .models import CoursePayment
    from django.db.models import Sum

    payments = CoursePayment.objects.filter(
        student=student
    ).select_related('course')

    total_amount = payments.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    total_paid = Decimal('0')
    for p in payments:
        paid = p.transactions.filter(
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_paid += paid

    return {
        'payments': payments,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'remaining': total_amount - total_paid,
    }

