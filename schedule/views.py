from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule
from .forms import ScheduleForm
from teachers.models import Teacher
from students.models import Student


@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(
        is_active=True
    ).select_related('course', 'teacher', 'teacher__user')

    # Guruh bo'yicha filter
    group = request.GET.get('group')
    if group:
        schedules = schedules.filter(group=group)

    # O'qituvchi bo'yicha filter
    teacher_id = request.GET.get('teacher')
    if teacher_id:
        schedules = schedules.filter(teacher_id=teacher_id)

    # Semestr bo'yicha filter
    semester = request.GET.get('semester')
    if semester:
        schedules = schedules.filter(semester=semester)

    # Haftalik ko'rinish — DAY_CHOICES inglizcha
    weekly_schedule = {}
    for day_num, day_name in Schedule.DAY_CHOICES:
        weekly_schedule[day_name] = schedules.filter(day_of_week=day_num)

    groups = Schedule.objects.values_list('group', flat=True).distinct()
    teachers = Teacher.objects.select_related('user').all()
    semesters = Schedule.objects.values_list('semester', flat=True).distinct()

    return render(request, 'schedule/schedule_list.html', {
        'weekly_schedule': weekly_schedule,
        'groups': groups,
        'teachers': teachers,
        'semesters': semesters,
        'selected_group': group,
        'selected_teacher': teacher_id,
        'selected_semester': semester,
    })


@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadval muvaffaqiyatli qo'shildi!")
            return redirect('schedule:list')
    else:
        form = ScheduleForm()

    return render(request, 'schedule/schedule_form.html', {'form': form})


@login_required
def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadval yangilandi!")
            return redirect('schedule:list')
    else:
        form = ScheduleForm(instance=schedule)

    return render(request, 'schedule/schedule_form.html', {
        'form': form,
        'schedule': schedule,
    })


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)

    if request.method == 'POST':
        schedule.delete()
        messages.success(request, "Jadval o'chirildi!")
        return redirect('schedule:list')

    return render(request, 'schedule/schedule_confirm_delete.html', {
        'schedule': schedule
    })


@login_required
def teacher_schedule(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)

    # related_name='schedules' — endi teacher.schedules.filter(...)
    schedules = teacher.schedules.filter(
        is_active=True
    ).select_related('course').order_by('day_of_week', 'start_time')

    weekly_schedule = {}
    for day_num, day_name in Schedule.DAY_CHOICES:
        weekly_schedule[day_name] = schedules.filter(day_of_week=day_num)

    return render(request, 'schedule/teacher_schedule.html', {
        'teacher': teacher,
        'weekly_schedule': weekly_schedule,
    })


@login_required
def student_schedule(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # O'quvchi yozilgan kurslar
    enrolled_courses = student.enrollment_set.filter(
        status='active'
    ).values_list('course_id', flat=True)

    # Shu kurslarning jadvali — related_name='schedules' ishlatiladi
    schedules = Schedule.objects.filter(
        course_id__in=enrolled_courses,
        is_active=True
    ).select_related('course', 'teacher', 'teacher__user')

    weekly_schedule = {}
    for day_num, day_name in Schedule.DAY_CHOICES:
        weekly_schedule[day_name] = schedules.filter(day_of_week=day_num)

    return render(request, 'schedule/student_schedule.html', {
        'student': student,
        'weekly_schedule': weekly_schedule,
    })

