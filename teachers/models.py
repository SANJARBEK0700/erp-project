from django.db import models
from django.conf import settings


class Teacher(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    teacher_id = models.CharField(
        max_length=20,
        unique=True
    )

    specialization = models.CharField(
        max_length=200
    )

    degree = models.CharField(
        max_length=100
    )

    experience_years = models.IntegerField(
        default=0
    )

    hire_date = models.DateField(
        null=True,
        blank=True
    )

    department = models.CharField(
        max_length=100
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_full_time = models.BooleanField(
        default=True
    )

    office_room = models.CharField(
        max_length=20,
        blank=True
    )

    working_hours = models.IntegerField(
        default=40
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.teacher_id}"