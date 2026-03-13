"""
accounts/forms.py
Team Lead mas'uliyati: Autentifikatsiya va profil form-lari
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

from .models import CustomUser


class LoginForm(AuthenticationForm):
    """Email va parol bilan kirish formi."""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email manzilingiz',
            'autofocus': True,
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolingiz',
        }),
        label="Parol"
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Eslab qolish"
    )

    error_messages = {
        'invalid_login': "Email yoki parol noto'g'ri. Qaytadan urinib ko'ring.",
        'inactive': "Bu hisob faol emas.",
    }


class AdminCreateUserForm(UserCreationForm):
    """
    Admin tomonidan yangi foydalanuvchi yaratish formi.
    Mustaqil register yo'q — faqat admin yaratadi.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        }),
        label="Email"
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ism',
        }),
        label="Ism"
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiya',
        }),
        label="Familiya"
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rol"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dastlabki parol (kamida 8 belgi)',
        }),
        label="Dastlabki parol"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang',
        }),
        label="Parolni tasdiqlash"
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Bu email allaqachon tizimda mavjud.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# Orqaga muvofiqliq uchun alias
RegisterForm = AdminCreateUserForm


class ProfileEditForm(forms.ModelForm):
    """Foydalanuvchi profilini tahrirlash formi."""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone', 'bio', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998 90 123 45 67'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            max_size = 2 * 1024 * 1024  # 2 MB
            if avatar.size > max_size:
                raise ValidationError("Rasm hajmi 2 MB dan oshmasligi kerak.")
        return avatar


class CustomPasswordChangeForm(PasswordChangeForm):
    """Parolni o'zgartirish formi."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Joriy parol"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Yangi parol"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Yangi parolni tasdiqlash"
    )
