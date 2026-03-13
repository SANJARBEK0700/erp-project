from django.urls import path

from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('<int:pk>/', views.assignment_detail, name='detail'),
    path('create/', views.assignment_create, name='create'),
    path('<int:pk>/update/', views.assignment_update, name='update'),
    path('<int:pk>/delete/', views.assignment_delete, name='delete'),
    path('<int:pk>/submit/', views.submission_create, name='submit'),
    path('submission/<int:pk>/grade/', views.submission_grade, name='grade'),
]