from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("message", "actor", "action", "object_type", "created_at")
    list_filter = ("action", "object_type", "created_at")
    search_fields = ("message", "actor__username")
