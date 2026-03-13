from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from notifications.tasks import send_new_assignment_email



def assignment_list(request):
    assignments = Assignment.objects.filter(
        is_active=True
    ).select_related('course', 'teacher').order_by('-created_at')

    context = {
        'assignments': assignments
    }
    return render(request, 'assignments/assignment_list.html', context)


def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submissions = assignment.submissions.all().select_related('student')

    user_submission = None
    if hasattr(request.user, 'student'):
        user_submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user.student
        ).first()

    context = {
        'assignment': assignment,
        'submissions': submissions,
        'user_submission': user_submission,
    }
    return render(request, 'assignments/assignment_detail.html', context)




def assignment_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        course_id = request.POST.get('course')
        due_date = request.POST.get('due_date')
        max_score = request.POST.get('max_score', 100)
        assignment_type = request.POST.get('assignment_type')
        allow_late = request.POST.get('allow_late') == 'on'
        attachment = request.FILES.get('attachment')

        if not title or not course_id or not due_date or not assignment_type:
            messages.error(request, "Majburiy maydonlarni to'ldiring.")
            return render(request, 'assignments/assignment_form.html')

        assignment = Assignment.objects.create(
            title=title,
            description=description,
            course_id=course_id,
            due_date=due_date,
            max_score=max_score,
            assignment_type=assignment_type,
            allow_late=allow_late,
            attachment=attachment,
            teacher=request.user.teacher
        )

        enrolled_students = assignment.course.enrollments.filter(
            status='active'
        ).select_related('student__user')

        for enrollment in enrolled_students:
            send_new_assignment_email.delay(
                student_email=enrollment.student.user.email,
                student_name=enrollment.student.user.get_full_name(),
                assignment_title=assignment.title,
                course_title=assignment.course.title,
                due_date=str(assignment.due_date)
            )

        messages.success(request, f"'{assignment.title}' vazifasi yaratildi!")
        return redirect('assignments:detail', pk=assignment.pk)

    return render(request, 'assignments/assignment_form.html')


def assignment_update(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == 'POST':
        assignment.title = request.POST.get('title', assignment.title)
        assignment.description = request.POST.get('description', assignment.description)
        assignment.due_date = request.POST.get('due_date', assignment.due_date)
        assignment.max_score = request.POST.get('max_score', assignment.max_score)
        assignment.assignment_type = request.POST.get('assignment_type', assignment.assignment_type)
        assignment.allow_late = request.POST.get('allow_late') == 'on'

        if request.FILES.get('attachment'):
            assignment.attachment = request.FILES.get('attachment')

        assignment.save()
        messages.success(request, f"'{assignment.title}' vazifasi yangilandi!")
        return redirect('assignments:detail', pk=assignment.pk)

    context = {
        'assignment': assignment
    }
    return render(request, 'assignments/assignment_form.html', context)


def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == 'POST':
        title = assignment.title
        assignment.delete()
        messages.success(request, f"'{title}' vazifasi o'chirildi.")
        return redirect('assignments:list')

    context = {
        'assignment': assignment
    }
    return render(request, 'assignments/assignment_confirm_delete.html', context)


# ==================== SUBMISSION VIEWS ====================

def submission_create(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if timezone.now() > assignment.due_date and not assignment.allow_late:
        messages.error(request, "Vazifa muddati o'tib ketgan, topshirish mumkin emas.")
        return redirect('assignments:detail', pk=pk)

    if request.method == 'POST':
        text_answer = request.POST.get('text_answer', '')
        file = request.FILES.get('file')

        is_late = timezone.now() > assignment.due_date

        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=request.user.student,
            defaults={
                'text_answer': text_answer,
                'file': file,
                'status': 'submitted',
                'is_late': is_late,
            }
        )

        if not created:
            submission.text_answer = text_answer
            if file:
                submission.file = file
            submission.is_late = is_late
            submission.save()

        messages.success(request, "Vazifa muvaffaqiyatli topshirildi!")
        return redirect('assignments:detail', pk=pk)

    context = {
        'assignment': assignment
    }
    return render(request, 'assignments/submission_form.html', context)


def submission_grade(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback', '')

        if not score:
            messages.error(request, "Ball kiritish majburiy.")
            return render(request, 'assignments/submission_grade.html', {'submission': submission})

        if int(score) > submission.assignment.max_score:
            messages.error(request, f"Ball {submission.assignment.max_score} dan oshmasligi kerak.")
            return render(request, 'assignments/submission_grade.html', {'submission': submission})

        submission.score = score
        submission.feedback = feedback
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.graded_by = request.user.teacher
        submission.save()

        messages.success(request, "Baholash muvaffaqiyatli saqlandi!")
        return redirect('assignments:detail', pk=submission.assignment.pk)

    context = {
        'submission': submission
    }
    return render(request, 'assignments/submission_grade.html', context)