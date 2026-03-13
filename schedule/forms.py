from django import forms
from .models import Schedule


class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule
        fields = [
            'course',
            'teacher',
            'day_of_week',
            'start_time',
            'end_time',
            'room',
            'group',
            'semester',
            'is_active',
        ]

        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'teacher': forms.Select(attrs={
                'class': 'form-control'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'room': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: A-101'
            }),
            'group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: G-1'
            }),
            'semester': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: 2024-1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        """
        To'qnashuv tekshiruvi:
        1. Xona bir vaqtda band bo'lmasligi kerak
        2. O'qituvchi bir vaqtda ikki joyda bo'lmasligi kerak
        """
        cleaned_data = super().clean()
        day_of_week = cleaned_data.get('day_of_week')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')
        teacher = cleaned_data.get('teacher')
        semester = cleaned_data.get('semester')

        # Barcha fieldlar to'ldirilganida tekshirish
        if all([day_of_week is not None, start_time, end_time, semester]):

            # Vaqt mantiqiy tekshiruvi
            if start_time >= end_time:
                raise forms.ValidationError(
                    "Tugash vaqti boshlanish vaqtidan katta bo'lishi kerak!"
                )

            # Mavjud jadvallar — o'zini exclude qilish
            existing = Schedule.objects.filter(
                day_of_week=day_of_week,
                semester=semester,
                is_active=True,
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            # Vaqt kesishuvini topish
            time_conflict = existing.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            # 1. Xona to'qnashuvi
            if room and time_conflict.filter(room=room).exists():
                raise forms.ValidationError(
                    f"'{room}' xonasi bu vaqtda band! "
                    f"Boshqa xona yoki vaqt tanlang."
                )

            # 2. O'qituvchi to'qnashuvi
            if teacher and time_conflict.filter(teacher=teacher).exists():
                raise forms.ValidationError(
                    f"O'qituvchi bu vaqtda boshqa dars o'tmoqda! "
                    f"Boshqa vaqt tanlang."
                )

        return cleaned_data