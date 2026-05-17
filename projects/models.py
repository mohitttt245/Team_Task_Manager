from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_projects",
        on_delete=models.CASCADE,
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if self.created_by_id and not self.created_by.is_admin_role:
            raise ValidationError({
                "created_by": "Only admins can create projects."
            })

    @property
    def progress_percentage(self):
        total_tasks = self.tasks.count()
        if not total_tasks:
            return 0
        completed = self.tasks.filter(status="DONE").count()
        return int((completed / total_tasks) * 100)

    def __str__(self):
        return self.name
