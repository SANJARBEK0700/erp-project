import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.permissions import admin_required, teacher_required
from .services import DashboardAnalyticsService, ExportService


@login_required
@admin_required
def analytics_overview(request):
    service = DashboardAnalyticsService()

    context = {
        'overview_stats': service.get_overview_stats(),
        'attendance_trend': json.dumps(service.get_attendance_trend(days=30)),
        'grade_distribution': json.dumps(service.get_grade_distribution()),
        'top_students': service.get_top_students(limit=10),
        'course_stats': service.get_course_enrollment_stats(),
        'low_attendance': service.get_low_attendance_students(threshold=75),
    }
    return render(request, 'analytics/overview.html', context)


@login_required
@admin_required
def analytics_attendance(request):
    """Davomat analitikasi sahifasi."""
    days = int(request.GET.get('days', 30))
    trend = DashboardAnalyticsService.get_attendance_trend(days=days)
    low = DashboardAnalyticsService.get_low_attendance_students()

    context = {
        'attendance_trend': json.dumps(trend),
        'low_attendance_students': low,
        'days': days,
    }
    return render(request, 'analytics/attendance.html', context)


@login_required
@admin_required
def analytics_grades(request):
    context = {
        'grade_distribution': json.dumps(DashboardAnalyticsService.get_grade_distribution()),
        'top_students': DashboardAnalyticsService.get_top_students(20),
    }
    return render(request, 'analytics/grades.html', context)
@login_required
@admin_required
def api_attendance_chart(request):
    days = int(request.GET.get('days', 30))
    data = DashboardAnalyticsService.get_attendance_trend(days=days)
    return JsonResponse(data)


@login_required
@admin_required
def api_grade_chart(request):
    data = DashboardAnalyticsService.get_grade_distribution()
    return JsonResponse(data)


@login_required
@admin_required
def api_overview_stats(request):
    data = DashboardAnalyticsService.get_overview_stats()
    return JsonResponse(data)


@login_required
@admin_required
def export_students_excel(request):
    excel_data = ExportService.export_students_to_excel()
    if excel_data:
        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"students_{timezone.now().strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Eksport uchun openpyxl kutubxonasi kerak.", status=500)


@login_required
@admin_required
def export_attendance_csv(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return HttpResponse("course_id parametri kerak.", status=400)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    csv_data = ExportService.export_attendance_to_csv(
        course_id=course_id,
        start_date=start_date,
        end_date=end_date
    )

    response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="attendance_{course_id}.csv"'
    return response