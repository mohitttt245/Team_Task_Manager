from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from projects.models import Project


class Task(models.Model):
    STATUS_TODO = "TODO"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_DONE = "DONE"

    PRIORITY_LOW = "LOW"
    PRIORITY_MEDIUM = "MEDIUM"
    PRIORITY_HIGH = "HIGH"

    STATUS_CHOICES = (
        (STATUS_TODO, "Todo"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    )

    PRIORITY_CHOICES = (
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "-created_at")

    def clean(self):
        super().clean()
        if self.assigned_to:
            if not self.project.team_members.filter(pk=self.assigned_to.pk).exists():
                raise ValidationError({"assigned_to": "Assigned user must belong to the selected project team."})
            if not self.assigned_to.is_member_role:
                raise ValidationError({"assigned_to": "Tasks can only be assigned to members."})

    @property
    def is_overdue(self):
        return self.due_date < timezone.localdate() and self.status != self.STATUS_DONE

    def __str__(self):
        return self.title
