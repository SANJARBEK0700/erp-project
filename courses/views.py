from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment, CourseMaterial



@login_required
def course_list(request):
    courses = Course.objects.filter(status='active').select_related('teacher')
    context = {
        'courses': courses
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    materials = course.materials.all().order_by('order')
    enrollments = course.enrollments.filter(status='active')
    is_enrolled = False

    if hasattr(request.user, 'student'):
        is_enrolled = Enrollment.objects.filter(
            student=request.user.student,
            course=course
        ).exists()

    context = {
        'course': course,
        'materials': materials,
        'enrollments': enrollments,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_create(request):
    if not request.user.role in ['admin', 'teacher']:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q.")
        return redirect('courses:list')

    if request.method == 'POST':
        title = request.POST.get('title')
        code = request.POST.get('code')
        description = request.POST.get('description')
        category = request.POST.get('category')
        max_students = request.POST.get('max_students', 30)
        credit_hours = request.POST.get('credit_hours', 3)
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        status = request.POST.get('status', 'upcoming')
        thumbnail = request.FILES.get('thumbnail')

        if not title or not code or not category:
            messages.error(request, "Majburiy maydonlarni to'ldiring.")
            return render(request, 'courses/course_form.html')

        if Course.objects.filter(code=code).exists():
            messages.error(request, "Bu kod allaqachon mavjud.")
            return render(request, 'courses/course_form.html')

        course = Course.objects.create(
            title=title,
            code=code,
            description=description,
            category=category,
            max_students=max_students,
            credit_hours=credit_hours,
            start_date=start_date,
            end_date=end_date,
            status=status,
            thumbnail=thumbnail,
            teacher=getattr(request.user, 'teacher', None)
        )
        messages.success(request, f"'{course.title}' kursi muvaffaqiyatli yaratildi!")
        return redirect('courses:detail', pk=course.pk)

    return render(request, 'courses/course_form.html')


@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not request.user.role in ['admin', 'teacher']:
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q.")
        return redirect('courses:list')

    if request.method == 'POST':
        course.title = request.POST.get('title', course.title)
        course.code = request.POST.get('code', course.code)
        course.description = request.POST.get('description', course.description)
        course.category = request.POST.get('category', course.category)
        course.max_students = request.POST.get('max_students', course.max_students)
        course.credit_hours = request.POST.get('credit_hours', course.credit_hours)
        course.start_date = request.POST.get('start_date') or course.start_date
        course.end_date = request.POST.get('end_date') or course.end_date
        course.status = request.POST.get('status', course.status)

        if request.FILES.get('thumbnail'):
            course.thumbnail = request.FILES.get('thumbnail')

        course.save()
        messages.success(request, f"'{course.title}' kursi muvaffaqiyatli yangilandi!")
        return redirect('courses:detail', pk=course.pk)

    context = {
        'course': course
    }
    return render(request, 'courses/course_form.html', context)


@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not request.user.role == 'admin':
        messages.error(request, "Faqat admin kursni o'chira oladi.")
        return redirect('courses:list')

    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f"'{title}' kursi o'chirildi.")
        return redirect('courses:list')

    context = {
        'course': course
    }
    return render(request, 'courses/course_confirm_delete.html', context)


# ==================== ENROLLMENT VIEWS ====================

@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not hasattr(request.user, 'student'):
        messages.error(request, "Faqat o'quvchilar kursga yozila oladi.")
        return redirect('courses:detail', pk=pk)

    if course.status != 'active':
        messages.error(request, "Bu kurs hozir yozilish uchun ochiq emas.")
        return redirect('courses:detail', pk=pk)

    current_enrollment_count = course.enrollments.filter(status='active').count()
    if current_enrollment_count >= course.max_students:
        messages.error(request, "Kurs to'lgan, joy qolmagan.")
        return redirect('courses:detail', pk=pk)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user.student,
        course=course,
        defaults={'status': 'active'}
    )

    if created:
        messages.success(request, f"'{course.title}' kursiga muvaffaqiyatli yozildingiz!")
    else:
        messages.info(request, "Siz bu kursga allaqachon yozilgansiz.")

    return redirect('courses:detail', pk=pk)


@login_required
def course_unenroll(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not hasattr(request.user, 'student'):
        return redirect('courses:detail', pk=pk)

    enrollment = Enrollment.objects.filter(
        student=request.user.student,
        course=course
    ).first()

    if enrollment:
        enrollment.status = 'dropped'
        enrollment.save()
        messages.success(request, f"'{course.title}' kursidan chiqib ketdingiz.")
    else:
        messages.error(request, "Siz bu kursga yozilmagansiz.")

    return redirect('courses:detail', pk=pk)