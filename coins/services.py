from django.db import transaction


# Coin miqdorlari — bir joyda sozlash uchun
COIN_RULES = {
    # Davomat
    'attendance_present': 10,
    'attendance_late':     5,
    'attendance_excused':  2,
    'attendance_absent':   0,

    # Baholar
    'grade_A': 50,
    'grade_B': 40,
    'grade_C': 30,
    'grade_D': 10,
    'grade_F':  0,
}


def award_attendance_coin(attendance_obj):
    """
    Davomat belgilanganida coin berish
    attendance_obj — Attendance modeli
    """
    from .models import CoinBalance, CoinTransaction

    status = attendance_obj.status
    reason_key = f'attendance_{status}'
    amount = COIN_RULES.get(reason_key, 0)

    # absent yoki 0 coin bo'lsa — yozmaymiz
    if amount == 0:
        return

    with transaction.atomic():
        # atomic — ikkalasi birga saqlanadi yoki ikkalasi ham saqlanmaydi

        # Balansni olish yoki yaratish
        balance, created = CoinBalance.objects.get_or_create(
            student=attendance_obj.student,
            defaults={'total_coins': 0}
        )
        balance.total_coins += amount
        balance.save()

        # Tarix yozish
        CoinTransaction.objects.create(
            student=attendance_obj.student,
            amount=amount,
            reason=reason_key,
            description=(
                f"{attendance_obj.course.title} — "
                f"{attendance_obj.date}"
            ),
            attendance=attendance_obj,
        )


def award_grade_coin(submission_obj):
    """
    Baho qo'yilganida coin berish
    submission_obj — Submission modeli (assignments app)
    """
    from .models import CoinBalance, CoinTransaction

    score = submission_obj.score
    max_score = submission_obj.assignment.max_score

    if score is None or max_score == 0:
        return

    # Foizga ko'ra harf baho aniqlash
    percentage = (score / max_score) * 100

    if percentage >= 90:
        reason_key = 'grade_A'
    elif percentage >= 80:
        reason_key = 'grade_B'
    elif percentage >= 70:
        reason_key = 'grade_C'
    elif percentage >= 60:
        reason_key = 'grade_D'
    else:
        reason_key = 'grade_F'

    amount = COIN_RULES.get(reason_key, 0)

    if amount == 0:
        return

    with transaction.atomic():
        balance, created = CoinBalance.objects.get_or_create(
            student=submission_obj.student,
            defaults={'total_coins': 0}
        )
        balance.total_coins += amount
        balance.save()

        CoinTransaction.objects.create(
            student=submission_obj.student,
            amount=amount,
            reason=reason_key,
            description=(
                f"{submission_obj.assignment.title} — "
                f"{score}/{max_score} ball"
            ),
            submission=submission_obj,
        )