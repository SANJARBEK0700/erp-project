from django.urls import path
from . import views

app_name = 'coins'

urlpatterns = [
    # /coins/rating/          — tizim reytingi
    path('rating/', views.system_rating, name='system_rating'),

    # /coins/rating/G-1/      — guruh reytingi
    path('rating/<str:group>/', views.group_rating, name='group_rating'),

    # /coins/student/5/       — o'quvchi coin tarixi
    path('student/<int:student_id>/', views.student_coin_history, name='history'),
]