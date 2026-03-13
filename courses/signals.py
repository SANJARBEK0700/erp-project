from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='courses.Enrollment')
def create_payment_on_enrollment(sender, instance, created, **kwargs):
    """
    O'quvchi kursga yozilganida CoursePayment avtomatik yaratish.
    Kurs narxi Course modelida bo'lishi kerak.
    """
    if created and instance.status == 'active':
        course = instance.course
        student = instance.student

        # Course modelida price field bo'lishi kerak
        # Umid qo'shishi kerak — courses/models.py ga
        if hasattr(course, 'price') and course.price:
            from apps.payments.services import create_course_payment
            create_course_payment(
                student=student,
                course=course,
                total_amount=course.price,
            )