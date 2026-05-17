from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from core.current_user import get_current_user
from projects.models import Project
from tasks.models import Task

from .models import ActivityLog


def create_activity(instance, action, message, metadata=None):
    actor = get_current_user()
    if actor is not None and not actor.is_authenticated:
        actor = None
    ActivityLog.objects.create(
        actor=actor,
        action=action,
        object_type=instance.__class__.__name__.lower(),
        object_id=instance.pk or 0,
        message=message,
        metadata=metadata or {},
    )


@receiver(pre_save, sender=Task)
def cache_previous_task_state(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous = Task.objects.filter(pk=instance.pk).values("status", "title").first()
    if previous:
        instance._previous_status = previous["status"]
        instance._previous_title = previous["title"]


@receiver(post_save, sender=Project)
def log_project_save(sender, instance, created, **kwargs):
    if created:
        create_activity(
            instance,
            "create",
            f"Project '{instance.name}' was created.",
        )
    else:
        create_activity(
            instance,
            "update",
            f"Project '{instance.name}' was updated.",
        )


@receiver(post_delete, sender=Project)
def log_project_delete(sender, instance, **kwargs):
    create_activity(
        instance,
        "delete",
        f"Project '{instance.name}' was deleted.",
    )


@receiver(post_save, sender=Task)
def log_task_save(sender, instance, created, **kwargs):
    metadata = {
        "project_id": instance.project_id,
        "assigned_to_id": instance.assigned_to_id,
        "status": instance.status,
        "priority": instance.priority,
    }
    if created:
        create_activity(
            instance,
            "create",
            f"Task '{instance.title}' was created for project '{instance.project.name}'.",
            metadata,
        )
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status and previous_status != instance.status:
        create_activity(
            instance,
            "status_update",
            f"Task '{instance.title}' moved from {previous_status.replace('_', ' ').title()} to {instance.status.replace('_', ' ').title()}.",
            metadata,
        )
    else:
        create_activity(
            instance,
            "update",
            f"Task '{instance.title}' was updated.",
            metadata,
        )


@receiver(post_delete, sender=Task)
def log_task_delete(sender, instance, **kwargs):
    create_activity(
        instance,
        "delete",
        f"Task '{instance.title}' was deleted.",
        {
            "project_id": instance.project_id,
            "assigned_to_id": instance.assigned_to_id,
        },
    )
