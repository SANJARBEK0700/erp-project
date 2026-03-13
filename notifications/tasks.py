from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# ==================== ASSIGNMENT TASKS ====================

@shared_task
def send_new_assignment_email(student_email, student_name, assignment_title, course_title, due_date):
    """
    O'quvchiga yangi vazifa haqida email yuboradi.
    O'qituvchi vazifa yaratganda ishga tushadi.
    """
    send_mail(
        subject=f"Yangi vazifa: {assignment_title}",
        message=f"""
Assalomu alaykum, {student_name}!

'{course_title}' kursida yangi vazifa qo'shildi.

Vazifa: {assignment_title}
Muddat: {due_date}

Tizimga kiring va vazifani ko'ring.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student_email],
        fail_silently=False,
    )


@shared_task
def send_submission_graded_email(student_email, student_name, assignment_title, score, max_score, feedback):
    """
    O'quvchiga vazifasi baholanganligi haqida email yuboradi.
    O'qituvchi baholash qilganda ishga tushadi.
    """
    send_mail(
        subject=f"Vazifangiz baholandi: {assignment_title}",
        message=f"""
Assalomu alaykum, {student_name}!

'{assignment_title}' vazifangiz baholandi.

Ball: {score}/{max_score}
Izoh: {feedback if feedback else "Izoh yo'q"}

Tizimga kiring va natijani ko'ring.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student_email],
        fail_silently=False,
    )


# ==================== ENROLLMENT TASKS ====================

@shared_task
def send_enrollment_approved_email(student_email, student_name, course_title):
    """
    O'quvchiga kursga qabul qilinganligi haqida email yuboradi.
    Admin enrollment ni tasdiqlagan da ishga tushadi.
    """
    send_mail(
        subject=f"Kursga qabul qilindingiz: {course_title}",
        message=f"""
Assalomu alaykum, {student_name}!

Siz '{course_title}' kursiga muvaffaqiyatli qabul qilindingiz.

Tizimga kiring va kurs materiallarini ko'rishni boshlang.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student_email],
        fail_silently=False,
    )



@shared_task
def send_attendance_warning_email(student_email, student_name, course_title, attendance_percent):
    """
    O'quvchiga davomat ogohlantirish emaili yuboradi.
    Davomat 75% dan past bo'lganda ishga tushadi.
    """
    send_mail(
        subject=f"Davomat ogohlantirish: {course_title}",
        message=f"""
Assalomu alaykum, {student_name}!

'{course_title}' kursidagi davomatingiz past.

Joriy davomat: {attendance_percent}%
Minimal talab: 75%

Iltimos, darslarga qatnashishni kuchaytiring!
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student_email],
        fail_silently=False,
    )