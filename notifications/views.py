from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Notification



def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    )

    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


def notification_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect('notifications:list')


def notification_read_all(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    messages.success(request, "Barcha bildirishnomalar o'qildi.")
    return redirect('notifications:list')


def notification_delete(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    notification.delete()
    messages.success(request, "Bildirishnoma o'chirildi.")
    return redirect('notifications:list')