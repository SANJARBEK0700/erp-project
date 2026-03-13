from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.username


class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', 'Yaratish'),
        ('update', 'O\'zgartirish'),
        ('delete', 'O\'chirish'),
        ('login', 'Tizimga kirish'),
        ('logout', 'Tizimdan chiqish'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit log"
        verbose_name_plural = "Audit loglar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.action} | {self.created_at:%Y-%m-%d %H:%M}"