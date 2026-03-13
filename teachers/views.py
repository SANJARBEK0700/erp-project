from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Teacher
from .forms import TeacherForm


@login_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').all()

    query = request.GET.get('q')
    if query:
        teachers = teachers.filter(
            user__first_name__icontains=query
        ) | teachers.filter(
            user__last_name__icontains=query
        ) | teachers.filter(
            specialization__icontains=query
        )

    department = request.GET.get('department')
    if department:
        teachers = teachers.filter(department=department)

    departments = Teacher.objects.values_list(
        'department', flat=True
    ).distinct()

    return render(request, 'teacher/teacher_list.html', {
        'teachers': teachers,
        'query':  query,
        'departments': departments,
        'selected_department': department,
    })

@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    courses = teacher.course_set.filter(status='active')

    tatal_hours = sum(
        course.schedule_set.filter( teacher=teacher).count()
        for course in courses
    )

    return render(request, 'teacher/teacher_detail.html', {
        'teacher': teacher,
        'courses': courses,
        'total_hours': tatal_hours,
    })


@login_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "O'qituvchi mufaqiyatli qo'shildi")
            return redirect('teacher:list')
    else:
        form = TeacherForm()

    return render(request, "teachers/teacher_form.html", {'form': form})


@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Malumotlar yangilandi")
            return redirect("teachers/teacher_form.html", {
                'form': form,
                'teacher': teacher,
            })

@login_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.delete()
        messages.success(request, "O'qituvchi o'chirldi")
        return redirect("teachers:list")

    return redirect(request, 'teacher/teacher_delete.html', {
        'teacher': teacher
    })


def teacher_workload(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    courses = teacher.course_set.filter(status='active')

    workload_data = []
    total_weekly_hours = 0

    for course in courses:
        schedule_count = course.schedule_set.filter(teacher=teacher).count()
        workload_data.append({
            'course': course,
            'weekly_lessons': schedule_count,
        })
        total_weekly_hours += schedule_count

    return render(request, 'teachers/teacher_workload.html', {
        'teacher': teacher,
        'workload_data': workload_data,
        'total_weekly_hours': total_weekly_hours,
        'is_overloaded': total_weekly_hours > teacher.working_hours,
    })
