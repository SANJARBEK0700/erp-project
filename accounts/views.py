from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.utils.decorators import method_decorator

from .forms import LoginForm, RegisterForm, ProfileEditForm, CustomPasswordChangeForm
from .models import CustomUser, AuditLog
from .permissions import admin_required




class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)


            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)


            AuditLog.objects.create(
                user=user,
                action='login',
                description=f"{user.email} tizimga kirdi",
                ip_address=self._get_client_ip(request)
            )

            messages.success(request, f"Xush kelibsiz, {user.get_full_name()}!")
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)

        return render(request, self.template_name, {'form': form})

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class LogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                description=f"{request.user.email} tizimdan chiqdi"
            )
        logout(request)
        messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
        return redirect('accounts:login')


class AdminCreateUserView(View):
    template_name = 'auth/admin_create_user.html'

    @method_decorator(login_required)
    @method_decorator(admin_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='CustomUser',
                object_id=user.id,
                description=f"Admin tomonidan yangi foydalanuvchi yaratildi: {user.email} ({user.role})"
            )
            messages.success(
                request,
                f"{user.get_full_name()} ({user.get_role_display()}) muvaffaqiyatli yaratildi. "
                f"Login: {user.email}"
            )
            return redirect('accounts:user_list')

        return render(request, self.template_name, {'form': form})



@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    if user.is_admin:
        context.update(_get_admin_dashboard_data())
        template = 'dashboard/admin_dashboard.html'

    elif user.is_teacher:
        context.update(_get_teacher_dashboard_data(user))
        template = 'dashboard/teacher_dashboard.html'

    else:  # student
        context.update(_get_student_dashboard_data(user))
        template = 'dashboard/student_dashboard.html'

    return render(request, template, context)


def _get_admin_dashboard_data():
    from django.db.models import Count
    from django.utils import timezone
    import datetime

    data = {}
    try:
        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.courses.models import Course
        from apps.attendance.models import Attendance

        today = timezone.now().date()
        data = {
            'total_students': Student.objects.filter(status='active').count(),
            'total_teachers': Teacher.objects.count(),
            'total_courses': Course.objects.filter(status='active').count(),
            'today_attendance': Attendance.objects.filter(date=today, status='present').count(),
            'recent_students': Student.objects.select_related('user').order_by('-enrolled_date')[:5],
            'active_courses': Course.objects.filter(status='active').select_related('teacher__user')[:5],
            'recent_logs': AuditLog.objects.select_related('user').order_by('-created_at')[:10],
        }
    except Exception:
        pass
    return data


def _get_teacher_dashboard_data(user):
    data = {}
    try:
        from apps.teachers.models import Teacher
        from apps.assignments.models import Submission
        from apps.schedule.models import Schedule
        from django.utils import timezone
        import datetime

        teacher = Teacher.objects.get(user=user)
        today = timezone.now().date()
        today_weekday = today.weekday()

        data = {
            'teacher': teacher,
            'my_courses': teacher.course_set.filter(status='active'),
            'today_schedule': Schedule.objects.filter(
                teacher=teacher,
                day_of_week=today_weekday,
                is_active=True
            ).select_related('course'),
            'ungraded_submissions': Submission.objects.filter(
                assignment__teacher=teacher,
                status='submitted'
            ).count(),
        }
    except Exception:
        pass
    return data


def _get_student_dashboard_data(user):
    data = {}
    try:
        from apps.students.models import Student
        from apps.assignments.models import Assignment
        from apps.schedule.models import Schedule
        from django.utils import timezone
        import datetime

        student = Student.objects.get(user=user)
        today = timezone.now().date()
        deadline_soon = today + datetime.timedelta(days=3)

        data = {
            'student': student,
            'enrolled_courses': student.enrollment_set.filter(status='active').select_related('course'),
            'upcoming_assignments': Assignment.objects.filter(
                course__enrollment__student=student,
                course__enrollment__status='active',
                due_date__date__lte=deadline_soon,
                due_date__date__gte=today,
                is_active=True,
            ).distinct()[:5],
            'today_schedule': Schedule.objects.filter(
                course__enrollment__student=student,
                day_of_week=today.weekday(),
                is_active=True
            ).select_related('course', 'teacher__user').distinct(),
        }
    except Exception:
        pass
    return data




@login_required
def profile_view(request):
    return render(request, 'auth/profile.html', {'profile_user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='CustomUser',
                object_id=request.user.id,
                description="Profil ma'lumotlari yangilandi"
            )
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'auth/profile_edit.html', {'form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'auth/password_change.html', {'form': form})




@login_required
@admin_required
def user_list_view(request):
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')

    users = CustomUser.objects.all().order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(
            first_name__icontains=search
        ) | users.filter(
            last_name__icontains=search
        ) | users.filter(
            email__icontains=search
        )

    context = {
        'users': users,
        'role_filter': role_filter,
        'search': search,
        'roles': CustomUser.ROLES,
    }
    return render(request, 'auth/user_list.html', context)


@login_required
@admin_required
def toggle_user_active(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user == request.user:
        messages.error(request, "O'zingizni deaktivatsiya qila olmaysiz.")
        return redirect('accounts:user_list')

    user.is_active = not user.is_active
    user.save()

    action = "faollashtirildi" if user.is_active else "deaktivatsiya qilindi"
    messages.success(request, f"{user.get_full_name()} {action}.")
    AuditLog.objects.create(
        user=request.user,
        action='update',
        model_name='CustomUser',
        object_id=user.id,
        description=f"Foydalanuvchi {action}: {user.email}"
    )
    return redirect('accounts:user_list')
