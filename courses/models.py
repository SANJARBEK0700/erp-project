from django.db import models


class Course(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('upcoming', 'Upcoming'),
    )

    title = models.CharField(
        max_length=200
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    credit_hours = models.IntegerField(
        default=3
    )

    category = models.CharField(
        max_length=100
    )

    max_students = models.IntegerField(
        default=30
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} ({self.code})"


from django.db import models


class Enrollment(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('dropped', 'Dropped'),
        ('completed', 'Completed'),
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    final_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    grade_letter = models.CharField(
        max_length=2,
        blank=True
    )

    is_approved = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} → {self.course}"