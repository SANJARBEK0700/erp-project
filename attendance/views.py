from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from students.models import Student
from courses.models import Course
from teachers.models import Teacher


@login_required
def attendance_list(request):
    # related_name yo'q bu yerda — to'g'ridan Attendance.objects ishlatamiz
    attendances = Attendance.objects.select_related(
        'student', 'student__user',
        'course',
        'marked_by', 'marked_by__user'
    ).all()

    # Kurs bo'yicha filter
    course_id = request.GET.get('course')
    if course_id:
        attendances = attendances.filter(course_id=course_id)

    # Sana bo'yicha filter
    date = request.GET.get('date')
    if date:
        attendances = attendances.filter(date=date)

    # Status bo'yicha filter — modeldan olamiz
    status = request.GET.get('status')
    if status:
        attendances = attendances.filter(status=status)

    courses = Course.objects.filter(status='active')

    return render(request, 'attendance/attendance_list.html', {
        'attendances': attendances,
        'courses': courses,
        'status_choices': Attendance.ATTENDANCE_STATUS,
        'selected_course': course_id,
        'selected_date': date,
        'selected_status': status,
    })


@login_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    # Kursga yozilgan o'quvchilar
    students = Student.objects.filter(
        enrollment__course=course,
        enrollment__status='active'
    ).select_related('user')

    if request.method == 'POST':
        date = request.POST.get('date')
        teacher = get_object_or_404(Teacher, user=request.user)
        saved_count = 0

        for student in students:
            status = request.POST.get(f'status_{student.pk}', 'absent')
            note = request.POST.get(f'note_{student.pk}', '')

            # unique_together = [student, course, date]
            # update_or_create — bor bo'lsa yangilaydi, yo'q bo'lsa yaratadi
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=date,
                defaults={
                    'status': status,
                    'note': note,
                    'marked_by': teacher,
                }
            )
            saved_count += 1

        messages.success(
            request,
            f"{saved_count} ta o'quvchi davomati belgilandi!"
        )
        return redirect('attendance:list')

    today = timezone.now().date()

    return render(request, 'attendance/mark_attendance.html', {
        'course': course,
        'students': students,
        'today': today,
        'status_choices': Attendance.ATTENDANCE_STATUS,
    })


@login_required
def attendance_report(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    students = Student.objects.filter(
        enrollment__course=course,
        enrollment__status='active'
    ).select_related('user')

    report_data = []
    warning_students = []

    for student in students:
        # related_name='attendances' — student.attendances.filter(...)
        records = student.attendances.filter(course=course)
        total = records.count()

        if total == 0:
            percentage = 0.0
        else:
            # SRS formulasi: present=1, late=0.5, absent/excused=0
            present_count = records.filter(status='present').count()
            late_count = records.filter(status='late').count()
            score = present_count + (late_count * 0.5)
            percentage = round((score / total) * 100, 1)

        report_data.append({
            'student': student,
            'percentage': percentage,
            'total': total,
            'present': records.filter(status='present').count(),
            'late': records.filter(status='late').count(),
            'absent': records.filter(status='absent').count(),
            'excused': records.filter(status='excused').count(),
        })

        if percentage < 75:
            warning_students.append(student)

    return render(request, 'attendance/attendance_report.html', {
        'course': course,
        'report_data': report_data,
        'warning_students': warning_students,
    })


@login_required
def student_attendance_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # related_name='attendances' ishlatamiz
    records = student.attendances.select_related(
        'course'
    ).order_by('-date')

    # O'quvchi yozilgan faol kurslar
    enrolled_courses = Course.objects.filter(
        enrollment__student=student,
        enrollment__status='active'
    )

    course_stats = []
    for course in enrolled_courses:
        course_records = student.attendances.filter(course=course)
        total = course_records.count()

        if total == 0:
            percentage = 0.0
        else:
            present_count = course_records.filter(status='present').count()
            late_count = course_records.filter(status='late').count()
            score = present_count + (late_count * 0.5)
            percentage = round((score / total) * 100, 1)

        course_stats.append({
            'course': course,
            'percentage': percentage,
            'is_warning': percentage < 75,
        })

    return render(request, 'attendance/student_attendance_detail.html', {
        'student': student,
        'records': records,
        'course_stats': course_stats,
    })