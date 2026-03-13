from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_overview, name='overview'),
    path('attendance/', views.analytics_attendance, name='attendance'),
    path('grades/', views.analytics_grades, name='grades'),


    path('api/attendance-chart/', views.api_attendance_chart, name='api_attendance'),
    path('api/grade-chart/', views.api_grade_chart, name='api_grades'),
    path('api/stats/', views.api_overview_stats, name='api_stats'),

    path('export/students/', views.export_students_excel, name='export_students'),
    path('export/attendance/', views.export_attendance_csv, name='export_attendance'),
]