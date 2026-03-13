from django.db import models
from django.conf import settings


class CoinBalance(models.Model):
    """
    Har bir o'quvchining umumiy coin balansi
    """
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='coin_balance'
    )
    total_coins = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.total_coins} coin"


class CoinTransaction(models.Model):
    """
    Har bir coin berilish tarixi — qachon, nima uchun, qancha
    """
    REASON_CHOICES = (
        ('attendance_present', 'Darsga keldi'),
        ('attendance_late',    'Kech qoldi'),
        ('attendance_excused', 'Sababli kelmadi'),
        ('grade_A', 'A baho'),
        ('grade_B', 'B baho'),
        ('grade_C', 'C baho'),
        ('grade_D', 'D baho'),
        ('grade_F', 'F baho'),
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='coin_transactions'
    )
    amount = models.IntegerField()
    # amount musbat = coin berildi, manfiy = coin olindi
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Qaysi davomat/baho sabab bo'lganini saqlash
    attendance = models.ForeignKey(
        'attendance.Attendance',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='coin_transactions'
    )
    submission = models.ForeignKey(
        'assignments.Submission',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='coin_transactions'
    )

    def __str__(self):
        return f"{self.student} | +{self.amount} | {self.get_reason_display()}"