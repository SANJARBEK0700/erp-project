from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # O'qituvchi
    path('teacher/<int:teacher_id>/', views.teacher_salary_detail, name='teacher_salary'),
    path('teacher/<int:teacher_id>/withdraw/', views.request_salary_withdrawal, name='withdraw'),
    path('withdrawals/', views.withdrawal_list, name='withdrawal_list'),
    path('withdrawals/<int:withdrawal_id>/approve/', views.approve_salary_withdrawal, name='approve'),

    # O'quvchi to'lovlari — YANGI
    path('student/<int:student_id>/', views.student_payments, name='student_payments'),
    path('create/', views.create_course_payment_view, name='create_payment'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/pay/', views.make_payment_view, name='make_payment'),

    # Admin
    path('courses/', views.course_payment_list, name='course_payments'),
]