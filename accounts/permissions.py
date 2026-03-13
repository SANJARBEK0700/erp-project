from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


try:
    from rest_framework.permissions import BasePermission as DRFBasePermission
    DRF_AVAILABLE = True
except ImportError:
    class DRFBasePermission:
        pass
    DRF_AVAILABLE = False




class IsAdmin(DRFBasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsTeacherOrAdmin(DRFBasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'teacher')
        )

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        if request.user.role == 'admin':
            return True
        owner = getattr(obj, 'teacher', None) or getattr(obj, 'user', None)
        if owner is None:
            return True
        if hasattr(owner, 'user'):
            return owner.user == request.user
        return owner == request.user


class IsStudent(DRFBasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'student'
        )

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        owner = getattr(obj, 'student', None) or getattr(obj, 'user', None)
        if owner is None:
            return True
        if hasattr(owner, 'user'):
            return owner.user == request.user
        return owner == request.user


class IsOwnerOrAdmin(DRFBasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if obj == request.user:
            return True
        return getattr(obj, 'user', None) == request.user


class IsAuthenticatedReadOnly(DRFBasePermission):
    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return request.user.role in ('admin', 'teacher')

class LoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin':
            raise PermissionDenied
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class TeacherRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ('admin', 'teacher'):
            raise PermissionDenied
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'student':
            raise PermissionDenied
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class OwnerOrAdminMixin(LoginRequiredMixin):
    owner_field = 'user'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.role == 'admin':
            return obj
        owner = getattr(obj, self.owner_field, None)
        if hasattr(owner, 'user'):
            owner = owner.user
        if owner != self.request.user:
            raise PermissionDenied
        return obj


================================================

def _redirect_to_login(request):
    from django.conf import settings
    login_url = getattr(settings, 'LOGIN_URL', '/login/')
    return redirect(f"{login_url}?next={request.get_full_path()}")


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)
        if request.user.role != 'admin':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)
        if request.user.role not in ('admin', 'teacher'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)
        if request.user.role != 'student':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _redirect_to_login(request)
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def owner_or_admin_required(get_owner_func):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _redirect_to_login(request)
            if request.user.role == 'admin':
                return view_func(request, *args, **kwargs)
            try:
                owner = get_owner_func(request, kwargs)
                if hasattr(owner, 'user'):
                    owner = owner.user
                if owner != request.user:
                    raise PermissionDenied
            except PermissionDenied:
                raise
            except Exception:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def user_has_role(user, *roles) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.role in roles


def user_can_manage_course(user, course) -> bool:
    if not user.is_authenticated:
        return False
    if user.role == 'admin':
        return True
    if user.role == 'teacher':
        teacher = getattr(user, 'teacher_profile', None)
        return teacher is not None and course.teacher == teacher
    return False


def user_can_view_student(user, student) -> bool:
    if not user.is_authenticated:
        return False
    if user.role == 'admin':
        return True
    if user.role == 'teacher':
        teacher = getattr(user, 'teacher_profile', None)
        if teacher is None:
            return False
        return student.enrollment_set.filter(
            course__teacher=teacher,
            status='active'
        ).exists()
    if user.role == 'student':
        student_profile = getattr(user, 'student_profile', None)
        return student_profile == student
    return False
