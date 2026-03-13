from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('create/', views.schedule_create, name='create'),
    path('<int:pk>/edit/', views.schedule_update, name='update'),
    path('<int:pk>/delete/', views.schedule_delete, name='delete'),
    path('teacher/<int:teacher_id>/', views.teacher_schedule, name='teacher'),
    path('student/<int:student_id>/', views.student_schedule, name='student'),
]