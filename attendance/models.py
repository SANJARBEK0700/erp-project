from django.db import models


class Attendance(models.Model):

    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_STATUS
    )

    marked_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendance'
    )

    marked_at = models.DateTimeField(
        auto_now_add=True
    )

    note = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        unique_together = ['student', 'course', 'date']

    def __str__(self):
        return f"{self.student} - {self.course} - {self.date}"