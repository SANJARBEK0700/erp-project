from django import forms
from .models import Student


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'user',
            'student_id',
            'group',
            'direction',
            'year_of_study',
            'date_of_birth',
            'address',
            'parent_name',
            'parent_phone',
            'gpa',
            'status',
        ]
        # enrolled_date — auto_now_add=True, shuning uchun fields ga kiritmadik

        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ST-001'
            }),
            'group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: G-1'
            }),
            'direction': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: Computer Science'
            }),
            'year_of_study': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'   # brauzerda date picker chiqadi
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998901234567'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '5'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_student_id(self):
        """
        student_id validatsiyasi:
        format ST-XXX bo'lishi kerak
        """
        student_id = self.cleaned_data.get('student_id')
        if not student_id.startswith('ST-'):
            raise forms.ValidationError(
                "Student ID 'ST-' bilan boshlanishi kerak. Masalan: ST-001"
            )
        return student_id

    def clean_gpa(self):
        """
        GPA 0 dan 5 gacha bo'lishi kerak
        """
        gpa = self.cleaned_data.get('gpa')
        if gpa is not None:
            if gpa < 0 or gpa > 5:
                raise forms.ValidationError(
                    "GPA 0.00 dan 5.00 gacha bo'lishi kerak!"
                )
        return gpa