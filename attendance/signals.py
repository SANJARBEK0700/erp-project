# Mavjud signallarga QO'SHIMCHA — fayl boshiga
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendance


# ... mavjud signallar ...


@receiver(post_save, sender=Attendance)
def give_coin_for_attendance(sender, instance, created, **kwargs):
    """
    Davomat belgilanganida coin berish
    """
    if created:
        from apps.coins.services import award_attendance_coin
        award_attendance_coin(instance)


# Mavjud signallarga shu qatorni qo'shamiz

@receiver(post_save, sender=Attendance)
def process_payment_on_attendance(sender, instance, created, **kwargs):
    """
    Davomat belgilanganida to'lov hisob-kitobini ishga tushirish
    """
    if created and instance.status in ['present', 'late']:
        from apps.payments.services import process_lesson_payment
        process_lesson_payment(instance)