from django.db.models import Count, Q
from django.utils import timezone

from projects.models import Project
from tasks.models import Task

from .models import ActivityLog


def get_recent_activities(limit=8):
    return ActivityLog.objects.select_related("actor")[:limit]


def get_admin_dashboard_data():
    today = timezone.localdate()
    task_queryset = Task.objects.select_related("project", "assigned_to")

    total_projects = Project.objects.count()
    total_tasks = task_queryset.count()
    completed_tasks = task_queryset.filter(status=Task.STATUS_DONE).count()
    pending_tasks = task_queryset.exclude(status=Task.STATUS_DONE).count()
    overdue_tasks = task_queryset.filter(due_date__lt=today).exclude(status=Task.STATUS_DONE).count()
    recent_activities = get_recent_activities()

    status_breakdown = list(
        task_queryset.values("status").annotate(total=Count("id")).order_by("status")
    )
    priority_breakdown = list(
        task_queryset.values("priority").annotate(total=Count("id")).order_by("priority")
    )

    overdue_task_list = task_queryset.filter(due_date__lt=today).exclude(status=Task.STATUS_DONE)[:6]
    project_progress = list(
        Project.objects.annotate(
            total_task_count=Count("tasks"),
            completed_task_count=Count("tasks", filter=Q(tasks__status=Task.STATUS_DONE)),
        )[:5]
    )

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "recent_activities": recent_activities,
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "overdue_task_list": overdue_task_list,
        "project_progress": project_progress,
    }


def get_member_dashboard_data(user):
    today = timezone.localdate()
    task_queryset = Task.objects.select_related("project").filter(assigned_to=user)

    my_tasks = task_queryset.count()
    completed_tasks = task_queryset.filter(status=Task.STATUS_DONE).count()
    pending_tasks = task_queryset.exclude(status=Task.STATUS_DONE).count()
    upcoming_deadlines = task_queryset.filter(due_date__gte=today).exclude(status=Task.STATUS_DONE)[:6]
    overdue_tasks = task_queryset.filter(due_date__lt=today).exclude(status=Task.STATUS_DONE).count()
    status_breakdown = list(
        task_queryset.values("status").annotate(total=Count("id")).order_by("status")
    )
    recent_activities = ActivityLog.objects.filter(
        Q(actor=user) | Q(metadata__assigned_to_id=user.id)
    ).select_related("actor")[:8]

    return {
        "my_tasks": my_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "upcoming_deadlines": upcoming_deadlines,
        "overdue_tasks": overdue_tasks,
        "status_breakdown": status_breakdown,
        "recent_activities": recent_activities,
        "today_focus": task_queryset.exclude(status=Task.STATUS_DONE).order_by("due_date")[:5],
    }
