from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CoinBalance
from apps.students.models import Student


@login_required
def system_rating(request):
    """
    Butun tizim bo'yicha reyting — top 50
    """
    ratings = CoinBalance.objects.select_related(
        'student', 'student__user'
    ).order_by('-total_coins')[:50]

    return render(request, 'coins/system_rating.html', {
        'ratings': ratings,
        'title': 'Tizim reytingi',
    })


@login_required
def group_rating(request, group):
    """
    Guruh bo'yicha reyting
    """
    ratings = CoinBalance.objects.filter(
        student__group=group
    ).select_related(
        'student', 'student__user'
    ).order_by('-total_coins')

    return render(request, 'coins/group_rating.html', {
        'ratings': ratings,
        'group': group,
        'title': f'{group} guruhi reytingi',
    })


@login_required
def student_coin_history(request, student_id):
    """
    O'quvchining coin tarixi
    """
    from apps.students.models import Student
    from django.shortcuts import get_object_or_404

    student = get_object_or_404(Student, pk=student_id)
    transactions = student.coin_transactions.order_by('-created_at')
    balance = getattr(student, 'coin_balance', None)

    return render(request, 'coins/student_history.html', {
        'student': student,
        'transactions': transactions,
        'balance': balance,
    })