from django.db import models


class CoursePayment(models.Model):
    """
    O'quvchining kurs uchun to'lovi
    O'quvchi kursga yozilganda to'lov amalga oshiriladi
    """
    STATUS_CHOICES = (
        ('pending',  'Kutilmoqda'),
        ('paid',     'To\'langan'),
        ('overdue',  'Muddati o\'tgan'),
        ('refunded', 'Qaytarilgan'),
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Kurs uchun to'liq narx
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    # Har bir dars narxi = total_amount / jami darslar soni
    per_lesson_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Bir o'quvchi bir kursga faqat bitta to'lov
        unique_together = ['student', 'course']
        verbose_name = "Kurs to'lovi"
        verbose_name_plural = "Kurs to'lovlari"

    def __str__(self):
        return (
            f"{self.student} | "
            f"{self.course} | "
            f"{self.total_amount} so'm"
        )


class TeacherEarning(models.Model):
    """
    O'qituvchi har bir dars uchun oladigan haq
    Davomat belgilanganida avtomatik yaratiladi
    """
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='teacher_earnings'
    )
    attendance = models.OneToOneField(
        'attendance.Attendance',
        on_delete=models.CASCADE,
        related_name='teacher_earning'
        # OneToOne — bir davomat uchun faqat bitta hisob-kitob
    )

    # Shu darsda necha o'quvchi kelgan
    students_present = models.IntegerField(default=0)

    # Shu darsda o'quvchilardan yig'ilgan umumiy summa
    total_lesson_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    # O'qituvchiga tushadigan 50%
    teacher_share = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    # Tizimda qoladigan 50%
    system_share = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'qituvchi daromadi"
        verbose_name_plural = "O'qituvchi daromadlari"

    def __str__(self):
        return (
            f"{self.teacher} | "
            f"{self.course} | "
            f"+{self.teacher_share} so'm"
        )


class TeacherSalaryBalance(models.Model):
    """
    O'qituvchining joriy oylik balansi
    Har oy boshlanganida reset qilinadi
    """
    teacher = models.OneToOneField(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='salary_balance'
    )
    # Shu oydagi umumiy daromad
    current_month_earning = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    # Jami umumiy daromad (barcha vaqt uchun)
    total_earning = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    last_updated = models.DateTimeField(auto_now=True)
    month = models.CharField(
        max_length=7,
        default='2024-01'
        # format: "2024-01", "2024-02"
    )

    def __str__(self):
        return (
            f"{self.teacher} | "
            f"Bu oy: {self.current_month_earning} so'm | "
            f"Jami: {self.total_earning} so'm"
        )


class SalaryWithdrawal(models.Model):
    """
    O'qituvchining oylik olish tarixi
    """
    STATUS_CHOICES = (
        ('pending',   'Kutilmoqda'),
        ('approved',  'Tasdiqlangan'),
        ('paid',      'To\'langan'),
        ('rejected',  'Rad etilgan'),
    )

    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.teacher} | "
            f"{self.amount} so'm | "
            f"{self.get_status_display()}"
        )

class PaymentTransaction(models.Model):
    """
    O'quvchining har bir to'lov operatsiyasi.
    Bir CoursePayment uchun bir necha marta to'lash mumkin
    (masalan, bo'lib to'lash)
    """
    PAYMENT_METHOD_CHOICES = (
        ('cash',        'Naqd pul'),
        ('card',        'Karta'),
        ('transfer',    'Bank o\'tkazmasi'),
        ('online',      'Online to\'lov'),
    )

    STATUS_CHOICES = (
        ('pending',   'Kutilmoqda'),
        ('success',   'Muvaffaqiyatli'),
        ('failed',    'Xato'),
        ('cancelled', 'Bekor qilindi'),
    )

    course_payment = models.ForeignKey(
        CoursePayment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    # To'langan summa — bo'lib to'lashda har safar turli summa
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # To'lov cheki raqami — naqd yoki karta uchun
    receipt_number = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True
    )

    # Kim qabul qildi (Admin/Kassir)
    received_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_payments'
    )

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.course_payment.student} | "
            f"{self.amount} so'm | "
            f"{self.get_payment_method_display()} | "
            f"{self.get_status_display()}"
        )