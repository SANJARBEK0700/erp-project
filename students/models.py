from django.db import models
from django.conf import settings


class Student(models.Model):

    YEAR_CHOICES = (
        (1, '1-kurs'),
        (2, '2-kurs'),
        (3, '3-kurs'),
        (4, '4-kurs'),
        (5, '5-kurs'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    student_id = models.CharField(
        max_length=20,
        unique=True
    )

    group = models.CharField(
        max_length=50
    )

    direction = models.CharField(
        max_length=100
    )

    year_of_study = models.IntegerField(
        choices=YEAR_CHOICES
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    parent_name = models.CharField(
        max_length=200,
        blank=True
    )

    parent_phone = models.CharField(
        max_length=20,
        blank=True
    )

    enrolled_date = models.DateField(
        auto_now_add=True
    )

    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"