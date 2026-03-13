from django import forms
from .models import Teacher


class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher
        fields = [
            'user',
            'teacher_id',
            'specialization',
            'degree',
            'experience_years',
            'hire_date',
            'department',
            'salary',
            'is_full_time',
            'office_room',
            'working_hours',
        ]

        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'teacher_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'TCH-001'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: Matematika'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: PhD, Magistr'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: Informatika kafedrasi'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_full_time': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'office_room': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: B-205'
            }),
            'working_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '80'
            }),
        }

    def clean_teacher_id(self):
        """
        teacher_id validatsiyasi:
        format TCH-XXX bo'lishi kerak
        """
        teacher_id = self.cleaned_data.get('teacher_id')
        if not teacher_id.startswith('TCH-'):
            raise forms.ValidationError(
                "Teacher ID 'TCH-' bilan boshlanishi kerak. Masalan: TCH-001"
            )
        return teacher_id

    def clean_working_hours(self):
        """
        Haftalik ish soati 0 dan 80 gacha
        """
        working_hours = self.cleaned_data.get('working_hours')
        if working_hours is not None:
            if working_hours < 0 or working_hours > 80:
                raise forms.ValidationError(
                    "Haftalik ish soati 0 dan 80 gacha bo'lishi kerak!"
                )
        return working_hours