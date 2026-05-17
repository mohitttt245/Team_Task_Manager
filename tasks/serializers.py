from rest_framework import serializers

from accounts.serializers import UserSerializer
from projects.serializers import ProjectSerializer

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        queryset=Task.assigned_to.field.related_model.objects.filter(role="MEMBER"),
        write_only=True,
    )
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(source="project", queryset=Task.project.field.related_model.objects.all(), write_only=True)
    created_by = UserSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "assigned_to",
            "assigned_to_id",
            "project",
            "project_id",
            "status",
            "priority",
            "due_date",
            "created_by",
            "created_at",
            "updated_at",
            "is_overdue",
        )


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("status",)
