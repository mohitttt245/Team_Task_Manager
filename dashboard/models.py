from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="activity_logs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=50)
    object_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    message = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.message
