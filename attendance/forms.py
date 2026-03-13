from django import forms
from .models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = [
            'student',
            'course',
            'date',
            'status',
            'marked_by',
            'note',
        ]

        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marked_by': forms.Select(attrs={
                'class': 'form-control'
            }),
            'note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Izoh (ixtiyoriy)'
            }),
        }

    def clean(self):
        """
        unique_together tekshiruvi:
        bir o'quvchi, bir kurs, bir sana uchun faqat bitta yozuv
        """
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        date = cleaned_data.get('date')

        if student and course and date:
            # Tahrirlashda o'zini o'zi bloklash xavfi — instance ni exclude
            qs = Attendance.objects.filter(
                student=student,
                course=course,
                date=date,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    f"{student} uchun {course} kursida "
                    f"{date} sanasida davomat allaqachon belgilangan!"
                )
        return cleaned_data