from django.db import models


class Assignment(models.Model):

    TYPE_CHOICES = (
        ('homework', 'Homework'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    due_date = models.DateTimeField()

    max_score = models.IntegerField(
        default=100
    )

    attachment = models.FileField(
        upload_to='assignments/',
        null=True,
        blank=True
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    is_active = models.BooleanField(
        default=True
    )

    allow_late = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.course}"





from django.db import models


class Submission(models.Model):

    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    )

    assignment = models.ForeignKey(
        'assignments.Assignment',
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    file = models.FileField(
        upload_to='submissions/',
        null=True,
        blank=True
    )

    text_answer = models.TextField(
        blank=True
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    score = models.IntegerField(
        null=True,
        blank=True
    )

    feedback = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    is_late = models.BooleanField(
        default=False
    )

    graded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    graded_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student} - {self.assignment}"