"""
accounts/urls.py
Team Lead mas'uliyati: Accounts URL konfiguratsiyasi
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.password_change_view, name='password_change'),

    # Admin: foydalanuvchilar boshqaruvi
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.AdminCreateUserView.as_view(), name='create_user'),
    path('users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
]
