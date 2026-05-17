from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source="actor.display_name", default="System")

    class Meta:
        model = ActivityLog
        fields = ("id", "actor", "action", "object_type", "object_id", "message", "created_at", "metadata")
