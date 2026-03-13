from django.db import models
from accounts.models import CustomUser


NOTIF_TYPES = [
    ('assignment_new', 'Yangi vazifa'),
    ('assignment_due', 'Vazifa muddati yaqinlashdi'),
    ('submission_graded', 'Vazifa baholandi'),
    ('enrollment_approved', 'Kursga qabul qilindi'),
    ('attendance_warning', 'Davomat ogohlantirish'),
    ('system', 'Tizim xabari'),
]


class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.get_full_name()} — {self.title}"
