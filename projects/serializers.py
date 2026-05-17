from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    team_members = UserSerializer(many=True, read_only=True)
    team_member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        source="team_members",
        queryset=Project.team_members.field.related_model.objects.filter(role="MEMBER"),
        required=False,
    )
    progress_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "team_members",
            "team_member_ids",
            "created_at",
            "updated_at",
            "progress_percentage",
        )

    def create(self, validated_data):
        team_members = validated_data.pop("team_members", [])
        project = Project.objects.create(**validated_data)
        project.team_members.set(team_members)
        return project

    def update(self, instance, validated_data):
        team_members = validated_data.pop("team_members", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if team_members is not None:
            instance.team_members.set(team_members)
        return instance
