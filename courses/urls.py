from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<int:pk>/', views.course_detail, name='detail'),
    path('create/', views.course_create, name='create'),
    path('<int:pk>/update/', views.course_update, name='update'),
    path('<int:pk>/delete/', views.course_delete, name='delete'),
    path('<int:pk>/enroll/', views.course_enroll, name='enroll'),
    path('<int:pk>/unenroll/', views.course_unenroll, name='unenroll'),
]