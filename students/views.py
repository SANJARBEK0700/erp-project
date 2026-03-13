from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import StudentForm

def atudent_list(request):
    students = Student.objects.select_related('user').all()

    query = request.GET.get('q')
    if query:
        students = students.filter(
            user__first_name__icontains=query
        ) | students.filter(
            user__last_name__icontains=query
        ) | students.filter(
            user__username__icontains=query
        ) | students.filter(
            student_id__icontains=query
        )

    status = request.GET.get('status')
    if status:
        students = students.filter(status=status)


    group = request.GET.get('group')
    if group:
        students = students.filter(group=group)

    groups = Student.objects.values_list('group', flat=True).distinct()
    return render(request, 'students/student_list.html', {
        'students': students,
        'query': query,
        'status_choices': Student.STATUS_CHOICES,
        'groups': groups,
        'selected_status': status,
        'selected_group': group,
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    return render(request, 'students/student_detail.html', {
        'student': student,
    })


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "O'quvchi muvaffaqiyatli qo'shildi!")
            return redirect('students:list')
    else:
        form = StudentForm()

    return render(request, 'students/student_form.html', {'form': form})



@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Ma'lumotlar yangilandi!")
            return redirect('students:detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {
        'form': form,
        'student': student,
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, "O'quvchi o'chirildi!")
        return redirect('students:list')

    return render(request, 'students/student_delete.html', {
        'student': student
    })

@login_required
def student_grades(request, pk):
    student = get_object_or_404(Student, pk=pk)

    enrollments = student.enrollment_set.select_related('course').all()

    return render(request, 'students/student_grades.html', {
        'student': student,
        'enrollments': enrollments,
    })


@login_required
def student_attendance(request, pk):
    student = get_object_or_404(Student, pk=pk)


    attendance_records = student.attendance_set.select_related(
        'course'
    ).order_by('-date')

    return render(request, 'students/student_attendance.html', {
        'student': student,
        'attendance_records': attendance_records,
    })









