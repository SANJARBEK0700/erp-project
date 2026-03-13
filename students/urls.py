from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.atudent_list, name='list'),
    path('create/', views.student_create, name='create'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.student_update, name='update'),
    path('<int:pk>/delete/', views.student_delete, name='delete'),
    path('<int:pk>/grades/', views.student_grades, name='grades'),
    path('<int:pk>/attendance/', views.student_attendance, name='attendance'),
]